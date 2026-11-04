package exp01;

import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.util.Arrays;

/**
 * One benchmark "fork": measures ONE (algorithm, input order, size) cell inside a
 * fresh JVM and prints the raw measurements as CSV lines on stdout.
 *
 * <pre>
 * java exp01.Worker ALGORITHM ORDER SIZE FORK BASE_SEED MEASURE_ITERS
 * </pre>
 *
 * Procedure of one fork:
 * <ol>
 * <li>Generate the input (deterministic from order, size, fork, base seed).</li>
 * <li><b>Warm-up</b>: sort fresh copies of the input one at a time until the JIT
 * compiler has settled (minimum number of sorts, minimum wall time, and - for sorts
 * that take longer than 100 us - the median of the last 5 sorts differs by less than
 * 5 % from the median of the 5 before).</li>
 * <li><b>Calibration</b>: choose a batch size B such that one timed batch takes about
 * 2 ms. Very small sorts (e.g. n = 100 sorted, about 100 ns) are far below the
 * resolution of {@code System.nanoTime()}, therefore a batch of B sorts is timed
 * and divided by B.</li>
 * <li><b>Measurement</b>: for each of MEASURE_ITERS iterations, create B fresh copies
 * (NOT timed), time the sorting of the B copies, then verify (NOT timed) that all
 * copies are sorted.</li>
 * </ol>
 * The sorter is called through the {@link Sorter} interface from a single call site,
 * and each JVM only ever runs one algorithm, so the call site stays monomorphic.
 */
public final class Worker {

	/** Target duration of one timed batch. */
	private static final long TARGET_BATCH_NS = 2_000_000L;

	/** Upper bound for B * n (array slots held in memory at once). */
	private static final long MAX_SLOTS = 2_000_000L;

	private static final int MIN_WARMUP_SORTS = 20;
	private static final long MIN_WARMUP_NS = 1_500_000_000L;
	private static final long MAX_WARMUP_NS = 40_000_000_000L;

	private Worker() {
	}

	static Sorter<Integer> createSorter(final String name) {
		switch (name) {
		case "PassPerItem":
			return new BubbleSortPassPerItem<>();
		case "UntilNoChange":
			return new BubbleSortUntilNoChange<>();
		case "WhileNeeded":
			return new BubbleSortWhileNeeded<>();
		default:
			throw new IllegalArgumentException("Unknown algorithm: " + name);
		}
	}

	private static boolean isSorted(final Integer[] a) {
		for (int i = 1; i < a.length; i++) {
			if (a[i - 1].compareTo(a[i]) > 0) {
				return false;
			}
		}
		return true;
	}

	/** Median of the sorts number (count-1-skip) down to (count-to), read from the ring buffer. */
	private static long recentMedian(final long[] ring, final int count, final int skip, final int to) {
		final int len = to - skip;
		final long[] copy = new long[len];
		for (int k = 0; k < len; k++) {
			copy[k] = ring[((count - 1 - skip - k) % ring.length + ring.length) % ring.length];
		}
		Arrays.sort(copy);
		return copy[len / 2];
	}

	private static long gcCount() {
		long total = 0;
		for (final GarbageCollectorMXBean b : ManagementFactory.getGarbageCollectorMXBeans()) {
			total += Math.max(0, b.getCollectionCount());
		}
		return total;
	}

	public static void main(final String[] args) {
		final String algorithm = args[0];
		final String order = args[1];
		final int n = Integer.parseInt(args[2]);
		final int fork = Integer.parseInt(args[3]);
		final long baseSeed = Long.parseLong(args[4]);
		final int measureIters = Integer.parseInt(args[5]);

		final Sorter<Integer> sorter = createSorter(algorithm);
		final Integer[] master = InputGenerator.generate(order, n, InputGenerator.seedFor(baseSeed, order, n, fork));

		// ---------------------------------------------------------------- warm-up
		final long[] warm = new long[16]; // ring buffer with the durations of the most recent sorts
		int warmCount = 0;
		long sink = 0;
		final long warmStart = System.nanoTime();
		boolean warmupTimedOut = false;
		while (true) {
			final Integer[] copy = master.clone();
			final long a = System.nanoTime();
			sorter.sort(copy);
			final long b = System.nanoTime();
			sink += copy[n / 2];
			warm[warmCount % warm.length] = b - a;
			warmCount++;
			final long elapsed = b - warmStart;
			if (elapsed > MAX_WARMUP_NS) {
				warmupTimedOut = true;
				break;
			}
			if (warmCount >= MIN_WARMUP_SORTS && elapsed >= MIN_WARMUP_NS) {
				final long recent = recentMedian(warm, warmCount, 0, 5);
				if (recent < 100_000L) {
					break; // tiny sorts: the minimum time is enough, ticks are too coarse to compare
				}
				final long before = recentMedian(warm, warmCount, 5, 10);
				if (Math.abs(recent - before) < 0.05 * before) {
					break;
				}
			}
		}

		// ------------------------------------------------------------ calibration
		final long perSort = Math.max(1L, recentMedian(warm, warmCount, 0, 5));
		final long maxBatch = Math.max(1L, MAX_SLOTS / n);
		final int batch = (int) Math.max(1L, Math.min(maxBatch, (TARGET_BATCH_NS + perSort - 1) / perSort));

		// --------------------------------------------------------------- measuring
		final Integer[][] copies = new Integer[batch][];
		System.gc();
		boolean allSorted = true;

		// two untimed batches so the batch loop itself is warm too
		for (int rep = 0; rep < 2; rep++) {
			for (int k = 0; k < batch; k++) {
				copies[k] = master.clone();
			}
			for (int k = 0; k < batch; k++) {
				sorter.sort(copies[k]);
			}
			sink += copies[0][0];
		}

		final StringBuilder out = new StringBuilder();
		for (int it = 0; it < measureIters; it++) {
			for (int k = 0; k < batch; k++) {
				copies[k] = master.clone(); // NOT timed
			}
			final long gcBefore = gcCount();
			final long t0 = System.nanoTime();
			for (int k = 0; k < batch; k++) {
				sorter.sort(copies[k]);
			}
			final long t1 = System.nanoTime();
			final long gcAfter = gcCount();

			for (int k = 0; k < batch; k++) { // NOT timed: correctness check
				if (!isSorted(copies[k])) {
					allSorted = false;
				}
			}
			sink += copies[batch - 1][n - 1];

			out.append(algorithm).append(',').append(order).append(',').append(n).append(',').append(fork).append(',')
					.append(it).append(',').append(batch).append(',')
					.append(String.format("%.3f", (t1 - t0) / (double) batch)).append(',')
					.append(gcAfter != gcBefore ? 1 : 0).append(',').append(warmCount).append(',')
					.append(warmupTimedOut ? 1 : 0).append('\n');
		}

		if (!allSorted) {
			System.err.println("ERROR: sorter produced an unsorted result: " + algorithm + " " + order + " " + n);
			System.exit(2);
		}
		System.out.print(out);
		System.out.flush();
		if (sink == 42L) { // keep 'sink' alive; practically never true
			System.err.println("sink");
		}
	}
}
