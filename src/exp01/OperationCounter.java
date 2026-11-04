package exp01;

/**
 * NOT part of the timed experiment. Counts, for every algorithm / input order / size,
 * the number of {@code compareTo} calls and the number of inversions of the input
 * (= number of swaps every bubble sort variant has to perform). This explains the
 * measured timings mechanically.
 *
 * <pre>
 * java exp01.OperationCounter OUTPUT.csv [extended]
 * </pre>
 *
 * With the argument {@code extended}, the additional orders and the small sizes of the
 * follow-up experiments are counted as well.
 */
public final class OperationCounter {

	private static final int[] SIZES = { 100, 1000, 2000, 5000, 10000, 20000 };

	/** Integer wrapper that counts comparisons. */
	private static final class Counted implements Comparable<Counted> {
		static long comparisons;
		final int value;

		Counted(final int value) {
			this.value = value;
		}

		@Override
		public int compareTo(final Counted o) {
			comparisons++;
			return Integer.compare(value, o.value);
		}
	}

	private OperationCounter() {
	}

	private static Sorter<Counted> create(final String name) {
		switch (name) {
		case "PassPerItem":
			return new BubbleSortPassPerItem<>();
		case "UntilNoChange":
			return new BubbleSortUntilNoChange<>();
		default:
			return new BubbleSortWhileNeeded<>();
		}
	}

	private static long inversions(final Integer[] a) {
		long inv = 0;
		for (int i = 0; i < a.length; i++) {
			for (int j = i + 1; j < a.length; j++) {
				if (a[i] > a[j]) {
					inv++;
				}
			}
		}
		return inv;
	}

	public static void main(final String[] args) throws Exception {
		final boolean extended = args.length > 1 && args[1].equals("extended");
		final java.util.List<String> orders = new java.util.ArrayList<>(java.util.Arrays.asList(InputGenerator.ORDERS));
		final java.util.List<Integer> sizes = new java.util.ArrayList<>();
		if (extended) {
			orders.addAll(java.util.Arrays.asList(InputGenerator.EXTRA_ORDERS));
			for (final int n : new int[] { 2, 3, 5, 10, 20, 50 }) {
				sizes.add(n);
			}
		}
		for (final int n : SIZES) {
			sizes.add(n);
		}
		final StringBuilder sb = new StringBuilder("algorithm,order,size,fork,comparisons,inversions\n");
		for (final String order : orders) {
			for (final int n : sizes) {
				for (int fork = 0; fork < 3; fork++) {
					final Integer[] input = InputGenerator.generate(order, n,
							InputGenerator.seedFor(20261104L, order, n, fork));
					final long inv = inversions(input);
					for (final String alg : new String[] { "PassPerItem", "UntilNoChange", "WhileNeeded" }) {
						final Counted[] c = new Counted[n];
						for (int i = 0; i < n; i++) {
							c[i] = new Counted(input[i]);
						}
						Counted.comparisons = 0;
						create(alg).sort(c);
						sb.append(alg).append(',').append(order).append(',').append(n).append(',').append(fork)
								.append(',').append(Counted.comparisons).append(',').append(inv).append('\n');
					}
				}
			}
		}
		java.nio.file.Files.write(java.nio.file.Paths.get(args[0]), sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
	}
}
