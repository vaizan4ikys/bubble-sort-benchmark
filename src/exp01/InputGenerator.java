package exp01;

import java.util.Random;

/**
 * Deterministic generator for the benchmark inputs.
 *
 * <p>All inputs are {@code Integer[]} of length {@code n}. The same
 * (order, n, seed) triple always yields exactly the same array, so that all three
 * algorithms are timed on identical data.
 */
final class InputGenerator {

	/** The input orders (levels of the factor "input order"). */
	static final String[] ORDERS = { "random", "sorted", "reversed", "nearly_local", "nearly_random", "few_unique" };

	/**
	 * Additional orders used by the follow-up experiments only (classic bubble-sort cases):
	 * {@code turtle} = sorted, but the smallest element is last (bubble sort moves it left by one
	 * position per pass); {@code rabbit} = sorted, but the largest element is first (it moves right
	 * in a single pass); {@code sorted_tail} = 90 % sorted prefix followed by 10 % random values
	 * (new items appended to a sorted list); {@code organ_pipe} = ascending, then descending;
	 * {@code sawtooth} = ascending runs of length 100.
	 */
	static final String[] EXTRA_ORDERS = { "turtle", "rabbit", "sorted_tail", "organ_pipe", "sawtooth" };

	/** Maximum distance of a swap in the {@code nearly_local} order. */
	private static final int LOCAL_DISTANCE = 10;

	/** Number of distinct values in the {@code few_unique} order. */
	private static final int UNIQUE_VALUES = 10;

	private InputGenerator() {
	}

	/**
	 * Derives a reproducible seed for one (order, size, fork) combination. The
	 * algorithm is deliberately NOT part of the seed: within one fork index, every
	 * algorithm receives the same data (paired design).
	 */
	static long seedFor(final long baseSeed, final String order, final int n, final int fork) {
		return baseSeed * 1_000_003L + order.hashCode() * 31L + n * 7L + fork;
	}

	static Integer[] generate(final String order, final int n, final long seed) {
		final Random rng = new Random(seed);
		final int[] v = new int[n];

		switch (order) {
		case "random":
			for (int i = 0; i < n; i++) {
				v[i] = rng.nextInt(Integer.MAX_VALUE);
			}
			break;
		case "sorted":
			for (int i = 0; i < n; i++) {
				v[i] = i;
			}
			break;
		case "reversed":
			for (int i = 0; i < n; i++) {
				v[i] = n - i;
			}
			break;
		case "nearly_local":
			for (int i = 0; i < n; i++) {
				v[i] = i;
			}
			for (int k = 0; k < Math.max(1, n / 20); k++) {
				final int i = rng.nextInt(n);
				final int j = Math.max(0, Math.min(n - 1, i + rng.nextInt(2 * LOCAL_DISTANCE + 1) - LOCAL_DISTANCE));
				swap(v, i, j);
			}
			break;
		case "nearly_random":
			for (int i = 0; i < n; i++) {
				v[i] = i;
			}
			for (int k = 0; k < Math.max(1, n / 20); k++) {
				swap(v, rng.nextInt(n), rng.nextInt(n));
			}
			break;
		case "few_unique":
			for (int i = 0; i < n; i++) {
				v[i] = rng.nextInt(UNIQUE_VALUES);
			}
			break;
		case "turtle":
			for (int i = 0; i < n; i++) {
				v[i] = i + 1;
			}
			v[n - 1] = 0;
			break;
		case "rabbit":
			for (int i = 0; i < n; i++) {
				v[i] = i;
			}
			v[0] = n;
			break;
		case "sorted_tail": {
			final int prefix = n - n / 10;
			for (int i = 0; i < n; i++) {
				v[i] = i < prefix ? i : rng.nextInt(n);
			}
			break;
		}
		case "organ_pipe":
			for (int i = 0; i < n; i++) {
				v[i] = Math.min(i, n - 1 - i);
			}
			break;
		case "sawtooth":
			for (int i = 0; i < n; i++) {
				v[i] = i % 100;
			}
			break;
		default:
			throw new IllegalArgumentException("Unknown input order: " + order);
		}

		// Box in array order, so the objects are laid out like in a "natural" program.
		final Integer[] result = new Integer[n];
		for (int i = 0; i < n; i++) {
			result[i] = Integer.valueOf(v[i]);
		}
		return result;
	}

	private static void swap(final int[] v, final int i, final int j) {
		final int t = v[i];
		v[i] = v[j];
		v[j] = t;
	}
}
