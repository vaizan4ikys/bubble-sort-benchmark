package exp01;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

/**
 * Functional tests of the three candidates. Timing results only mean something if all
 * candidates sort correctly, so we check:
 * <ol>
 * <li>EVERY permutation of arrays of length 0..7 (exhaustive),</li>
 * <li>random arrays of length up to 2000 against {@link Arrays#sort(Object[])},</li>
 * <li>all input orders used in the experiments,</li>
 * <li>stability (equal keys keep their original order),</li>
 * <li>that the input array is sorted in place (same array object, same elements).</li>
 * </ol>
 * Exit code 0 = all tests passed.
 *
 * <pre>
 * java exp01.CorrectnessTest
 * </pre>
 */
public final class CorrectnessTest {

	private static int checks;
	private static int failures;

	private CorrectnessTest() {
	}

	/** Element with a sort key and an original position (to test stability). */
	private static final class Item implements Comparable<Item> {
		final int key;
		final int id;

		Item(final int key, final int id) {
			this.key = key;
			this.id = id;
		}

		@Override
		public int compareTo(final Item o) {
			return Integer.compare(key, o.key);
		}
	}

	private static void expect(final boolean ok, final String what) {
		checks++;
		if (!ok) {
			failures++;
			if (failures <= 20) {
				System.out.println("FAIL: " + what);
			}
		}
	}

	private static void permutations(final int[] a, final int k, final List<int[]> out) {
		if (k == a.length) {
			out.add(a.clone());
			return;
		}
		for (int i = k; i < a.length; i++) {
			int t = a[k]; a[k] = a[i]; a[i] = t;
			permutations(a, k + 1, out);
			t = a[k]; a[k] = a[i]; a[i] = t;
		}
	}

	private static Integer[] box(final int[] v) {
		final Integer[] r = new Integer[v.length];
		for (int i = 0; i < v.length; i++) {
			r[i] = v[i];
		}
		return r;
	}

	public static void main(final String[] args) {
		for (final String alg : new String[] { "PassPerItem", "UntilNoChange", "WhileNeeded" }) {
			final Sorter<Integer> s = Worker.createSorter(alg);

			// 1. exhaustive permutations (with 0..7 distinct values)
			for (int len = 0; len <= 7; len++) {
				final int[] base = new int[len];
				for (int i = 0; i < len; i++) {
					base[i] = i;
				}
				final List<int[]> perms = new ArrayList<>();
				permutations(base, 0, perms);
				for (final int[] p : perms) {
					final Integer[] a = box(p);
					final Integer[] expected = a.clone();
					Arrays.sort(expected);
					s.sort(a);
					expect(Arrays.equals(a, expected), alg + " permutation " + Arrays.toString(p));
				}
			}

			// 2. random arrays, many lengths, with and without many duplicates
			final Random rng = new Random(12345);
			for (int trial = 0; trial < 600; trial++) {
				final int len = trial < 300 ? rng.nextInt(60) : rng.nextInt(2001);
				final int range = (trial % 3 == 0) ? 5 : 1_000_000;
				final int[] v = new int[len];
				for (int i = 0; i < len; i++) {
					v[i] = rng.nextInt(range);
				}
				final Integer[] a = box(v);
				final Integer[] expected = a.clone();
				Arrays.sort(expected);
				final Integer[] same = a;
				s.sort(a);
				expect(a == same && Arrays.equals(a, expected), alg + " random trial " + trial + " len " + len);
			}

			// 3. all input orders of the experiments
			final List<String> orders = new ArrayList<>(Arrays.asList(InputGenerator.ORDERS));
			orders.addAll(Arrays.asList(InputGenerator.EXTRA_ORDERS));
			for (final String order : orders) {
				for (final int n : new int[] { 1, 2, 3, 5, 10, 20, 100, 1000, 3000 }) {
					final Integer[] a = InputGenerator.generate(order, n, 99);
					final Integer[] expected = a.clone();
					Arrays.sort(expected);
					s.sort(a);
					expect(Arrays.equals(a, expected), alg + " order " + order + " n " + n);
				}
			}

			// 4. stability
			final Sorter<Item> si = alg.equals("PassPerItem") ? new BubbleSortPassPerItem<>()
					: alg.equals("UntilNoChange") ? new BubbleSortUntilNoChange<>() : new BubbleSortWhileNeeded<>();
			for (int trial = 0; trial < 100; trial++) {
				final int len = rng.nextInt(500);
				final Item[] items = new Item[len];
				for (int i = 0; i < len; i++) {
					items[i] = new Item(rng.nextInt(10), i);
				}
				si.sort(items);
				boolean stable = true;
				for (int i = 1; i < len; i++) {
					final boolean ordered = items[i - 1].key < items[i].key
							|| (items[i - 1].key == items[i].key && items[i - 1].id < items[i].id);
					stable &= ordered;
				}
				expect(stable, alg + " stability trial " + trial);
			}
		}
		System.out.println(checks + " checks, " + failures + " failures");
		System.exit(failures == 0 ? 0 : 1);
	}
}
