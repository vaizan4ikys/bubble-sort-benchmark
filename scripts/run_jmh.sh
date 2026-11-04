#!/bin/bash
# Builds and runs the JMH cross-check (needs Maven and network access for the first build).
# Result: results/ext_jmh/jmh.json and jmh.txt
cd "$(dirname "$0")/.." || exit 1
mkdir -p results/ext_jmh
cp src/exp01/Sorter.java src/exp01/BubbleSort*.java src/exp01/InputGenerator.java src/exp01/Worker.java jmh/src/main/java/exp01/
(cd jmh && mvn -q -B -DskipTests package) || { echo "JMH build failed"; exit 1; }
java -Xms2g -Xmx2g -XX:+UseSerialGC -jar jmh/target/benchmarks.jar \
  -f 3 -wi 5 -w 1s -i 10 -r 1s -rf json -rff results/ext_jmh/jmh.json | tee results/ext_jmh/jmh.txt
