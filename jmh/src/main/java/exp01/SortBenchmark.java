package exp01;

import java.util.concurrent.TimeUnit;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Level;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.OutputTimeUnit;
import org.openjdk.jmh.annotations.Param;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;

/**
 * Independent cross-check of the hand-written harness with JMH, the standard Java micro-benchmark
 * framework. Same sorters, same input generator and same data (fork 0 of the main experiment).
 * The array copy is done in a per-invocation setup, which JMH excludes from the measured time
 * (adequate here because every measured sort takes milliseconds).
 */
@State(Scope.Thread)
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MICROSECONDS)
public class SortBenchmark {

	@Param({ "PassPerItem", "UntilNoChange", "WhileNeeded" })
	public String algorithm;

	@Param({ "random", "reversed", "nearly_local" })
	public String order;

	@Param({ "5000", "20000" })
	public int size;

	private Sorter<Integer> sorter;
	private Integer[] master;
	private Integer[] work;

	@Setup(Level.Trial)
	public void setupTrial() {
		sorter = Worker.createSorter(algorithm);
		master = InputGenerator.generate(order, size, InputGenerator.seedFor(20261104L, order, size, 0));
	}

	@Setup(Level.Invocation)
	public void copy() {
		work = master.clone();
	}

	@Benchmark
	public Integer[] sort() {
		sorter.sort(work);
		return work;
	}
}
