package exp01;

import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.Locale;

/**
 * Generic variant of {@link Worker} used for the FOLLOW-UP experiments (element type
 * {@code String} instead of {@code Integer}). The measurement procedure is identical to
 * {@link Worker}; see there for a detailed description. {@link Worker} itself was left
 * untouched because it produced the main data set.
 *
 * <pre>
 * java exp01.ExtendedWorker TYPE ALGORITHM ORDER SIZE FORK BASE_SEED MEASURE_ITERS
 * </pre>
 *
 * TYPE is {@code Integer}, {@code String} or {@code PollutedInteger}. {@code String} elements are the zero-padded
 * decimal representation of exactly the same integers that {@code Integer} uses, so the
 * very same permutations are sorted; only the cost of {@code compareTo} differs.
 */
public final class ExtendedWorker {

	private static final long TARGET_BATCH_NS = 2_000_000L;
	private static final long MAX_SLOTS = 2_000_000L;
	private static final int MIN_WARMUP_SORTS = 20;
	private static final long MIN_WARMUP_NS = 1_500_000_000L;
	private static final long MAX_WARMUP_NS = 40_000_000_000L;

	private ExtendedWorker() {
	}

	private static <T extends Comparable<T>> Sorter<T> createSorter(final String name) {
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

	private static <T extends Comparable<T>> boolean isSorted(final T[] a) {
		for (int i = 1; i < a.length; i++) {
			if (a[i - 1].compareTo(a[i]) > 0) {
				return false;
			}
		}
		return true;
	}

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
		final String type = args[0];
		final String algorithm = args[1];
		final String order = args[2];
		final int n = Integer.parseInt(args[3]);
		final int fork = Integer.parseInt(args[4]);
		final long baseSeed = Long.parseLong(args[5]);
		final int measureIters = Integer.parseInt(args[6]);

		final Integer[] ints = InputGenerator.generate(order, n, InputGenerator.seedFor(baseSeed, order, n, fork));
		switch (type) {
		case "Integer":
			measure(type, algorithm, order, n, fork, measureIters, ints);
			break;
		case "String":
			final String[] strings = new String[n];
			for (int i = 0; i < n; i++) {
				strings[i] = String.format("%010d", ints[i]);
			}
			measure(type, algorithm, order, n, fork, measureIters, strings);
			break;
		case "PollutedInteger":
			pollute(algorithm, Math.min(n, 1000));
			measure(type, algorithm, order, n, fork, measureIters, ints);
			break;
		default:
			throw new IllegalArgumentException("Unknown element type: " + type);
		}
	}

	/** A small user-defined element type, to make {@code compareTo} call sites megamorphic. */
	private static final class Box implements Comparable<Box> {
		final double key;

		Box(final double key) {
			this.key = key;
		}

		@Override
		public int compareTo(final Box o) {
			return Double.compare(key, o.key);
		}
	}

	/**
	 * Simulates a "polluted" JVM, as in a real application that sorts many different element
	 * types with the same library: before the measured {@code Integer} sorts, the same algorithm
	 * sorts Strings, Longs and user-defined objects for about 300 ms each. Afterwards the type
	 * profile of {@code compareTo} (and of the generic sort code) is megamorphic, so the JIT
	 * compiler can no longer inline {@code Integer.compareTo} as in the clean-JVM experiments.
	 */
	private static void pollute(final String algorithm, final int n) {
		final java.util.Random rng = new java.util.Random(7);
		final String[] strings = new String[n];
		final Long[] longs = new Long[n];
		final Box[] boxes = new Box[n];
		for (int i = 0; i < n; i++) {
			strings[i] = Integer.toString(rng.nextInt(1_000_000));
			longs[i] = rng.nextLong();
			boxes[i] = new Box(rng.nextDouble());
		}
		final Sorter<String> ss = createSorter(algorithm);
		final Sorter<Long> sl = createSorter(algorithm);
		final Sorter<Box> sb = createSorter(algorithm);
		final long deadline = System.nanoTime() + 900_000_000L;
		// interleave the types so every type is seen throughout the compilation of the sort code
		while (System.nanoTime() < deadline) {
			ss.sort(strings.clone());
			sl.sort(longs.clone());
			sb.sort(boxes.clone());
		}
	}

	@SuppressWarnings("unchecked")
	static <T extends Comparable<T>> void measure(final String type, final String algorithm,
			final String order, final int n, final int fork, final int measureIters, final T[] master) {
		final Sorter<T> sorter = createSorter(algorithm);

		// ---------------------------------------------------------------- warm-up
		final long[] warm = new long[16];
		int warmCount = 0;
		Object sink = null;
		final long warmStart = System.nanoTime();
		boolean warmupTimedOut = false;
		while (true) {
			final T[] copy = master.clone();
			final long a = System.nanoTime();
			sorter.sort(copy);
			final long b = System.nanoTime();
			sink = copy[n / 2];
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
					break;
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
		final T[][] copies = (T[][]) Array.newInstance(master.getClass(), batch);
		System.gc();
		boolean allSorted = true;

		for (int rep = 0; rep < 2; rep++) {
			for (int k = 0; k < batch; k++) {
				copies[k] = master.clone();
			}
			for (int k = 0; k < batch; k++) {
				sorter.sort(copies[k]);
			}
			sink = copies[0][0];
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
			sink = copies[batch - 1][n - 1];

			out.append(type).append(',').append(algorithm).append(',').append(order).append(',').append(n).append(',')
					.append(fork).append(',').append(it).append(',').append(batch).append(',')
					.append(String.format(Locale.ROOT, "%.3f", (t1 - t0) / (double) batch)).append(',')
					.append(gcAfter != gcBefore ? 1 : 0).append(',').append(warmCount).append(',')
					.append(warmupTimedOut ? 1 : 0).append('\n');
		}

		if (!allSorted) {
			System.err.println("ERROR: sorter produced an unsorted result: " + algorithm + " " + order + " " + n);
			System.exit(2);
		}
		System.out.print(out);
		System.out.flush();
		if (sink == null) {
			System.err.println("sink");
		}
	}
}
