package exp01;

/**
 * "Cold start" measurement: how long do the FIRST sort calls of a fresh JVM take, before the
 * JIT compiler has had time to optimise anything? This is the situation of a short-lived program
 * (a command-line tool, a serverless function) that sorts a few times and exits.
 *
 * <pre>
 * java exp01.ColdWorker ALGORITHM ORDER SIZE FORK BASE_SEED MAX_CALLS BUDGET_MS
 * </pre>
 *
 * Every call sorts a fresh copy of the input and is timed individually with
 * {@code System.nanoTime()} (no warm-up, no batching). Output rows:
 * {@code algorithm,order,size,fork,call,ns}. The run stops after MAX_CALLS calls or when the
 * cumulated sorting time exceeds BUDGET_MS.
 */
public final class ColdWorker {

	private ColdWorker() {
	}

	public static void main(final String[] args) {
		final String algorithm = args[0];
		final String order = args[1];
		final int n = Integer.parseInt(args[2]);
		final int fork = Integer.parseInt(args[3]);
		final long baseSeed = Long.parseLong(args[4]);
		final int maxCalls = Integer.parseInt(args[5]);
		final long budgetNs = Long.parseLong(args[6]) * 1_000_000L;

		final Sorter<Integer> sorter = Worker.createSorter(algorithm);
		final Integer[] master = InputGenerator.generate(order, n, InputGenerator.seedFor(baseSeed, order, n, fork));
		final StringBuilder out = new StringBuilder();
		long total = 0;
		long sink = 0;
		for (int call = 0; call < maxCalls && total < budgetNs; call++) {
			final Integer[] copy = master.clone();
			final long a = System.nanoTime();
			sorter.sort(copy);
			final long b = System.nanoTime();
			total += b - a;
			sink += copy[n / 2];
			out.append(algorithm).append(',').append(order).append(',').append(n).append(',').append(fork).append(',')
					.append(call).append(',').append(b - a).append('\n');
		}
		System.out.print(out);
		if (sink == 42L) {
			System.err.println("sink");
		}
	}
}
