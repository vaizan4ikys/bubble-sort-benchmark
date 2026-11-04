# Rule for re-measuring uncertain cells (fixed BEFORE looking at the main results)

After the main experiment (`results/full`, forks 0-9) has finished, every *(input order, input size)*
group with n >= 1 000 is checked against the criteria below. A group is **uncertain** if at least one of
them holds for at least one of its three algorithms:

1. **High variability:** the coefficient of variation between the 10 fork medians exceeds 5 %.
2. **Imprecise estimate:** the half-width of the 95 % t-confidence interval of the mean fork median exceeds
   3 % of that mean.
3. **Measurement problem:** a garbage collection happened inside any timed batch of the group, or a warm-up
   hit its time limit.
4. **Undecided hypothesis:** one of the pre-registered hypothesis checks (`analysis/out/main/hypothesis_cells.csv`)
   for that group is `inconclusive` (its confidence interval straddles the threshold).

Uncertain groups are measured again with **20 additional forks (fork ids 10-29)**, all three algorithms,
same procedure and settings, fresh input data (the fork id is part of the data seed). Their data is stored in
`results/remeasure/` and never overwrites the main data.

Reporting: the main analysis is always reported as is; the pooled analysis (10 + 20 forks for the re-measured groups)
is reported next to it, so the reader can see whether the extra data changed any conclusion. Because only
uncertain groups receive extra data, the pooled estimates are reported as a sensitivity analysis, not as a
replacement of the pre-planned main analysis. The same rule is applied once, to all groups, without exceptions.
