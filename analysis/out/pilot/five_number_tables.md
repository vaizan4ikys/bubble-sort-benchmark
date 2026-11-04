### random

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 5.24 µs | 7.82 µs | 8.07 µs | 8.33 µs | 8.47 µs |
| 100 | UntilNoChange | 9.04 µs | 9.37 µs | 9.45 µs | 9.53 µs | 9.69 µs |
| 100 | WhileNeeded | 4.60 µs | 4.74 µs | 5.53 µs | 5.64 µs | 6.07 µs |
| 1000 | PassPerItem | 821 µs | 825 µs | 827 µs | 847 µs | 872 µs |
| 1000 | UntilNoChange | 990 µs | 1.02 ms | 1.03 ms | 1.05 ms | 1.08 ms |
| 1000 | WhileNeeded | 602 µs | 614 µs | 618 µs | 632 µs | 654 µs |
| 5000 | PassPerItem | 19.9 ms | 20.1 ms | 20.2 ms | 20.6 ms | 21.9 ms |
| 5000 | UntilNoChange | 25.2 ms | 25.4 ms | 26.0 ms | 26.5 ms | 26.8 ms |
| 5000 | WhileNeeded | 15.1 ms | 15.3 ms | 15.3 ms | 15.4 ms | 15.6 ms |

### sorted

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 5.10 µs | 5.33 µs | 5.44 µs | 5.47 µs | 5.62 µs |
| 100 | UntilNoChange | 26.2 ns | 33.5 ns | 56.9 ns | 57.9 ns | 73.6 ns |
| 100 | WhileNeeded | 25.3 ns | 26.0 ns | 38.7 ns | 53.4 ns | 65.3 ns |
| 1000 | PassPerItem | 528 µs | 553 µs | 554 µs | 557 µs | 569 µs |
| 1000 | UntilNoChange | 392 ns | 565 ns | 569 ns | 574 ns | 604 ns |
| 1000 | WhileNeeded | 355 ns | 478 ns | 487 ns | 495 ns | 524 ns |
| 5000 | PassPerItem | 13.4 ms | 13.7 ms | 13.7 ms | 13.9 ms | 15.0 ms |
| 5000 | UntilNoChange | 1.27 µs | 2.83 µs | 2.89 µs | 2.91 µs | 3.03 µs |
| 5000 | WhileNeeded | 2.37 µs | 2.48 µs | 2.49 µs | 2.50 µs | 2.55 µs |

### reversed

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 7.45 µs | 10.2 µs | 10.3 µs | 10.5 µs | 10.9 µs |
| 100 | UntilNoChange | 15.6 µs | 15.7 µs | 15.8 µs | 15.9 µs | 16.2 µs |
| 100 | WhileNeeded | 9.39 µs | 9.84 µs | 9.95 µs | 9.98 µs | 10.3 µs |
| 1000 | PassPerItem | 971 µs | 997 µs | 999 µs | 1.01 ms | 1.04 ms |
| 1000 | UntilNoChange | 1.44 ms | 1.50 ms | 1.51 ms | 1.52 ms | 1.55 ms |
| 1000 | WhileNeeded | 1.07 ms | 1.08 ms | 1.08 ms | 1.09 ms | 1.12 ms |
| 5000 | PassPerItem | 24.5 ms | 24.6 ms | 24.7 ms | 25.0 ms | 29.1 ms |
| 5000 | UntilNoChange | 37.4 ms | 37.5 ms | 37.7 ms | 37.9 ms | 40.4 ms |
| 5000 | WhileNeeded | 26.6 ms | 27.0 ms | 27.1 ms | 27.2 ms | 27.4 ms |

### nearly sorted (local swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 5.84 µs | 6.22 µs | 6.26 µs | 6.35 µs | 6.46 µs |
| 100 | UntilNoChange | 854 ns | 944 ns | 1.18 µs | 1.47 µs | 1.52 µs |
| 100 | WhileNeeded | 565 ns | 602 ns | 668 ns | 683 ns | 807 ns |
| 1000 | PassPerItem | 560 µs | 589 µs | 593 µs | 595 µs | 607 µs |
| 1000 | UntilNoChange | 8.21 µs | 9.84 µs | 9.95 µs | 10.1 µs | 10.2 µs |
| 1000 | WhileNeeded | 8.83 µs | 9.01 µs | 9.13 µs | 9.55 µs | 9.68 µs |
| 5000 | PassPerItem | 14.5 ms | 14.5 ms | 14.6 ms | 14.8 ms | 16.7 ms |
| 5000 | UntilNoChange | 50.0 µs | 50.4 µs | 66.1 µs | 83.5 µs | 83.9 µs |
| 5000 | WhileNeeded | 48.0 µs | 49.1 µs | 65.4 µs | 82.9 µs | 83.6 µs |

### nearly sorted (random swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 6.44 µs | 6.62 µs | 6.74 µs | 6.80 µs | 7.04 µs |
| 100 | UntilNoChange | 5.74 µs | 5.87 µs | 7.22 µs | 8.80 µs | 8.84 µs |
| 100 | WhileNeeded | 2.69 µs | 3.45 µs | 3.91 µs | 4.39 µs | 4.43 µs |
| 1000 | PassPerItem | 629 µs | 640 µs | 642 µs | 646 µs | 661 µs |
| 1000 | UntilNoChange | 781 µs | 784 µs | 826 µs | 867 µs | 897 µs |
| 1000 | WhileNeeded | 430 µs | 445 µs | 450 µs | 460 µs | 467 µs |
| 5000 | PassPerItem | 15.8 ms | 16.0 ms | 16.1 ms | 16.4 ms | 17.9 ms |
| 5000 | UntilNoChange | 21.3 ms | 21.4 ms | 21.6 ms | 22.0 ms | 22.2 ms |
| 5000 | WhileNeeded | 11.3 ms | 11.4 ms | 11.5 ms | 11.6 ms | 12.0 ms |

### few unique values

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 6.46 µs | 8.59 µs | 8.74 µs | 8.76 µs | 8.89 µs |
| 100 | UntilNoChange | 7.64 µs | 8.80 µs | 8.87 µs | 8.98 µs | 9.30 µs |
| 100 | WhileNeeded | 5.29 µs | 5.37 µs | 5.44 µs | 5.50 µs | 5.65 µs |
| 1000 | PassPerItem | 995 µs | 1.01 ms | 1.01 ms | 1.02 ms | 1.11 ms |
| 1000 | UntilNoChange | 1.08 ms | 1.09 ms | 1.11 ms | 1.15 ms | 1.23 ms |
| 1000 | WhileNeeded | 651 µs | 656 µs | 671 µs | 683 µs | 722 µs |
| 5000 | PassPerItem | 23.2 ms | 23.3 ms | 23.4 ms | 23.5 ms | 23.9 ms |
| 5000 | UntilNoChange | 25.1 ms | 25.4 ms | 25.6 ms | 25.7 ms | 25.9 ms |
| 5000 | WhileNeeded | 15.7 ms | 15.7 ms | 15.8 ms | 15.8 ms | 15.9 ms |

