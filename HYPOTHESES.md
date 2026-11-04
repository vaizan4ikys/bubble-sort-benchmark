# Hypotheses (written BEFORE any measurement was taken)

This file was committed to git before the benchmark harness was written or run;
the commit timestamp is the evidence. It must not be edited afterwards.

## Setting

* Independent variables
  * **Algorithm** (3 levels): `PassPerItem`, `UntilNoChange`, `WhileNeeded`
  * **Input order** (6 levels): `random`, `sorted`, `reversed`, `nearly_local`
    (sorted array in which 5 % of the elements were swapped with a neighbour at
    most 10 positions away), `nearly_random` (sorted array in which n/20 random
    pairs, anywhere in the array, were swapped), `few_unique` (random, only
    10 distinct values)
  * **Input size n** (6 levels): 100, 1 000, 2 000, 5 000, 10 000, 20 000
* Dependent variable: **running time of one `sort` call** (nanoseconds, ratio scale).
* "Median time" below means the median over the per-fork medians of the measured times.
* "Faster by x %" means `1 - t_A / t_B` computed on those medians.

## Reasoning behind the hypotheses (from reading the code only)

* `PassPerItem` always performs n passes of n-1 comparisons (about n^2), regardless of the input.
* `UntilNoChange` stops after the first pass without a swap: one pass for sorted input,
  roughly "largest left-displacement of any element" passes otherwise.
* `WhileNeeded` also stops early *and* shrinks every pass to the position of the last
  swap of the previous pass, so it skips the already-sorted tail.
* All three perform exactly the same swaps (one per inversion); they differ only in the
  number of comparisons.

## Hypotheses

**H1 (sorted input).** For n >= 1 000, on `sorted` input the median time of `PassPerItem`
is at least 100x the median time of `UntilNoChange` and at least 100x that of `WhileNeeded`.
(IV: algorithm; DV: running time.)

**H2 (random input).** For n >= 5 000, on `random` input `WhileNeeded` has the lowest
median running time of the three algorithms, while `UntilNoChange` and `PassPerItem`
differ from each other by less than 15 %. (IV: algorithm; DV: running time.)

**H3 (reversed input).** For n >= 5 000, on `reversed` input `WhileNeeded` is at least
10 % faster (median running time) than both `UntilNoChange` and `PassPerItem`.
(IV: algorithm; DV: running time.)

**H4 (locally disturbed input).** For n >= 5 000, on `nearly_local` input both
`UntilNoChange` and `WhileNeeded` are at least 10x faster (median running time) than
`PassPerItem`. (IV: algorithm; DV: running time.)

**H5 (growth with size).** For `random` input, doubling n from 10 000 to 20 000 multiplies
the median running time by a factor between 3.3 and 4.7 for every algorithm (quadratic
growth). For `sorted` input, the same doubling multiplies the median running time of
`UntilNoChange` and `WhileNeeded` by a factor below 2.6 (linear growth), but that of
`PassPerItem` by a factor between 3.3 and 4.7. (IV: input size and algorithm; DV: running time.)

**H6 (recommendation / non-inferiority).** In no combination of input order and size
n >= 1 000 is `WhileNeeded` slower than `UntilNoChange` or `PassPerItem` by more than 5 %
(median running time). If this holds, `WhileNeeded` is recommended. (IV: algorithm,
input order, input size; DV: running time.)

## What would falsify these

Each hypothesis is stated with a numeric threshold, so a single clear violation in the
stated range of conditions (not explained by measurement noise, judged with the 95 %
confidence intervals) counts as a falsification of that hypothesis. We will report
falsified hypotheses as such.
