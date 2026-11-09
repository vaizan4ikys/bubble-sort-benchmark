package exp01;

import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.util.Arrays;
import java.util.Locale;

/**
 * Variant of {@link Worker} with a longer, <b>adaptive warm-up of the batch loop itself</b>.
 * It was written after a review of the main data set found that, for very short sorts
 * (e.g. sorted input, n = 1 000 or 20 000), the speed changed by up to a factor 2 INSIDE a fork,
 * after about 20 timed batches: the single-sort warm-up of {@link Worker} does not exercise the
 * loop that sorts a whole batch, and that loop (with the sort inlined into it) was probably compiled
 * while it was being timed (compilation events were not recorded). {@link Worker} itself was left unchanged because it produced the
 * main data set.
 *
 * <pre>
 * java exp01.SteadyWorker ALGORITHM ORDER SIZE FORK BASE_SEED MEASURE_ITERS
 * </pre>
 *
 * Procedure: identical to {@link Worker} (input, single-sort warm-up, calibration of the batch size), then
 * <ol>
 * <li><b>Stabilisation</b>: whole batches are run (copies created, batch sorted) through the SAME method
 * {@link #timeBatch} that the measurement uses, until the median batch time of the last W rounds differs
 * by less than 3 % from that of the W rounds before, for 5 consecutive rounds, after at least MIN_ROUNDS
 * rounds (W = 50 and MIN_ROUNDS = 400 for batches shorter than 20 ms; W = 5 and MIN_ROUNDS = 10 otherwise;
 * the 400 rounds come from a test that found the last level shift of the affected cells after about 250 rounds).
 * For short batches the stabilisation also lasts at least {@code exp01.minStabMs} milliseconds of wall-clock time
 * (default 4000; the steady-state run of the report used 8000), because later level shifts were observed several
 * seconds after the start of the loop; they are probably caused by JIT compilations that finish in the background
 * (compilation events were not recorded). The stabilisation is limited to 15 s of batch time; the flag {@code stab_converged} tells whether the
 * criterion was met.</li>
 * <li><b>Measurement</b>: as in {@link Worker}, with the same {@link #timeBatch} method.</li>
 * </ol>
 * Output columns: those of {@link Worker} plus {@code stab_rounds,stab_converged}.
 */
public final class SteadyWorker {

	private static final long TARGET_BATCH_NS = 2_000_000L;
	private static final long MAX_SLOTS = 2_000_000L;
	private static final int MIN_WARMUP_SORTS = 20;
	private static final long MIN_WARMUP_NS = 1_500_000_000L;
	private static final long MAX_WARMUP_NS = 40_000_000_000L;
	private static final long MAX_STAB_NS = 15_000_000_000L;
	private static final long SHORT_BATCH_NS = 20_000_000L;
	private static final double STAB_TOLERANCE = 0.03;
	private static final int STAB_CONSECUTIVE = 5;
	/** Minimum WALL-CLOCK time of the stabilisation for short batches (JIT compilations finish in the background). */
	private static final long MIN_STAB_WALL_NS = Long.getLong("exp01.minStabMs", 4000L) * 1_000_000L;

	private SteadyWorker() {
	}

	private static boolean isSorted(final Integer[] a) {
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

	private static long medianOf(final long[] hist, final int count, final int skip, final int len) {
		final long[] copy = new long[len];
		for (int k = 0; k < len; k++) {
			copy[k] = hist[count - 1 - skip - k];
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

	/** Times the sorting of all copies of one batch. The only place where a batch is sorted. */
	static long timeBatch(final Sorter<Integer> sorter, final Integer[][] copies, final int batch) {
		final long t0 = System.nanoTime();
		for (int k = 0; k < batch; k++) {
			sorter.sort(copies[k]);
		}
		return System.nanoTime() - t0;
	}

	private static void refill(final Integer[][] copies, final Integer[] master, final int batch) {
		for (int k = 0; k < batch; k++) {
			copies[k] = master.clone();
		}
	}

	public static void main(final String[] args) {
		final String algorithm = args[0];
		final String order = args[1];
		final int n = Integer.parseInt(args[2]);
		final int fork = Integer.parseInt(args[3]);
		final long baseSeed = Long.parseLong(args[4]);
		final int measureIters = Integer.parseInt(args[5]);

		final Sorter<Integer> sorter = Worker.createSorter(algorithm);
		final Integer[] master = InputGenerator.generate(order, n, InputGenerator.seedFor(baseSeed, order, n, fork));

		// ---------------------------------------------- single-sort warm-up (as in Worker)
		final long[] warm = new long[16];
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
		final Integer[][] copies = new Integer[batch][];
		System.gc();

		// ---------------------------------------- stabilisation of the batch loop itself
		final boolean shortBatches = (long) batch * perSort < SHORT_BATCH_NS;
		final int window = shortBatches ? 50 : 5;
		final int minRounds = shortBatches ? 400 : 10;
		final int maxRounds = 100_000;
		final long[] hist = new long[maxRounds];
		int rounds = 0;
		int okRun = 0;
		long stabTime = 0;
		boolean converged = false;
		final long stabStart = System.nanoTime();
		while (rounds < maxRounds && stabTime < MAX_STAB_NS) {
			refill(copies, master, batch);
			final long t = timeBatch(sorter, copies, batch);
			sink += copies[0][0];
			hist[rounds++] = t;
			stabTime += t;
			final boolean wallOk = !shortBatches || System.nanoTime() - stabStart >= MIN_STAB_WALL_NS;
			if (wallOk && rounds >= Math.max(minRounds, 2 * window)) {
				final long recent = medianOf(hist, rounds, 0, window);
				final long before = medianOf(hist, rounds, window, window);
				okRun = Math.abs(recent - before) < STAB_TOLERANCE * before ? okRun + 1 : 0;
				if (okRun >= STAB_CONSECUTIVE) {
					converged = true;
					break;
				}
			}
		}

		// --------------------------------------------------------------- measuring
		boolean allSorted = true;
		final StringBuilder out = new StringBuilder();
		for (int it = 0; it < measureIters; it++) {
			refill(copies, master, batch); // NOT timed
			final long gcBefore = gcCount();
			final long t = timeBatch(sorter, copies, batch);
			final long gcAfter = gcCount();
			for (int k = 0; k < batch; k++) { // NOT timed: correctness check
				if (!isSorted(copies[k])) {
					allSorted = false;
				}
			}
			sink += copies[batch - 1][n - 1];
			out.append(algorithm).append(',').append(order).append(',').append(n).append(',').append(fork).append(',')
					.append(it).append(',').append(batch).append(',')
					.append(String.format(Locale.ROOT, "%.3f", t / (double) batch)).append(',')
					.append(gcAfter != gcBefore ? 1 : 0).append(',').append(warmCount).append(',')
					.append(warmupTimedOut ? 1 : 0).append(',').append(rounds).append(',').append(converged ? 1 : 0)
					.append('\n');
		}
		if (!allSorted) {
			System.err.println("ERROR: sorter produced an unsorted result: " + algorithm + " " + order + " " + n);
			System.exit(2);
		}
		System.out.print(out);
		System.out.flush();
		if (sink == 42L) {
			System.err.println("sink");
		}
	}
}
