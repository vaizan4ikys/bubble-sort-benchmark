### random

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 7.76 µs | 7.83 µs | 7.99 µs | 8.04 µs | 8.32 µs |
| 100 | UntilNoChange | 8.78 µs | 9.17 µs | 9.62 µs | 9.83 µs | 10.2 µs |
| 100 | WhileNeeded | 5.45 µs | 5.52 µs | 5.76 µs | 5.86 µs | 6.16 µs |
| 1000 | PassPerItem | 804 µs | 813 µs | 816 µs | 820 µs | 858 µs |
| 1000 | UntilNoChange | 982 µs | 1.00 ms | 1.02 ms | 1.03 ms | 1.10 ms |
| 1000 | WhileNeeded | 592 µs | 608 µs | 614 µs | 620 µs | 633 µs |
| 2000 | PassPerItem | 3.24 ms | 3.26 ms | 3.27 ms | 3.29 ms | 3.58 ms |
| 2000 | UntilNoChange | 3.90 ms | 4.02 ms | 4.08 ms | 4.10 ms | 4.18 ms |
| 2000 | WhileNeeded | 2.33 ms | 2.45 ms | 2.47 ms | 2.48 ms | 2.59 ms |
| 5000 | PassPerItem | 20.0 ms | 20.0 ms | 20.1 ms | 20.2 ms | 20.5 ms |
| 5000 | UntilNoChange | 24.6 ms | 25.1 ms | 25.3 ms | 25.4 ms | 26.6 ms |
| 5000 | WhileNeeded | 15.2 ms | 15.3 ms | 15.3 ms | 15.4 ms | 15.6 ms |
| 10000 | PassPerItem | 91.7 ms | 93.2 ms | 93.8 ms | 95.0 ms | 102 ms |
| 10000 | UntilNoChange | 106 ms | 108 ms | 109 ms | 110 ms | 111 ms |
| 10000 | WhileNeeded | 59.8 ms | 60.8 ms | 61.0 ms | 61.2 ms | 62.3 ms |
| 20000 | PassPerItem | 446 ms | 448 ms | 450 ms | 451 ms | 523 ms |
| 20000 | UntilNoChange | 483 ms | 489 ms | 491 ms | 492 ms | 501 ms |
| 20000 | WhileNeeded | 256 ms | 257 ms | 258 ms | 260 ms | 268 ms |

### sorted

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 4.89 µs | 5.53 µs | 5.54 µs | 5.56 µs | 5.63 µs |
| 100 | UntilNoChange | 25.5 ns | 25.8 ns | 25.8 ns | 26.1 ns | 27.6 ns |
| 100 | WhileNeeded | 25.0 ns | 25.1 ns | 25.2 ns | 25.3 ns | 25.8 ns |
| 1000 | PassPerItem | 551 µs | 552 µs | 553 µs | 560 µs | 628 µs |
| 1000 | UntilNoChange | 250 ns | 252 ns | 253 ns | 256 ns | 431 ns |
| 1000 | WhileNeeded | 264 ns | 267 ns | 268 ns | 273 ns | 497 ns |
| 2000 | PassPerItem | 2.19 ms | 2.19 ms | 2.20 ms | 2.21 ms | 2.40 ms |
| 2000 | UntilNoChange | 1.12 µs | 1.13 µs | 1.14 µs | 1.14 µs | 1.18 µs |
| 2000 | WhileNeeded | 931 ns | 973 ns | 980 ns | 984 ns | 1.00 µs |
| 5000 | PassPerItem | 13.6 ms | 13.6 ms | 13.6 ms | 13.7 ms | 13.8 ms |
| 5000 | UntilNoChange | 2.81 µs | 2.82 µs | 2.82 µs | 2.86 µs | 3.09 µs |
| 5000 | WhileNeeded | 2.33 µs | 2.42 µs | 2.42 µs | 2.43 µs | 2.58 µs |
| 10000 | PassPerItem | 58.2 ms | 62.9 ms | 63.9 ms | 64.8 ms | 66.7 ms |
| 10000 | UntilNoChange | 5.68 µs | 5.71 µs | 5.72 µs | 5.74 µs | 5.83 µs |
| 10000 | WhileNeeded | 4.88 µs | 4.90 µs | 4.91 µs | 4.94 µs | 5.31 µs |
| 20000 | PassPerItem | 223 ms | 223 ms | 223 ms | 224 ms | 237 ms |
| 20000 | UntilNoChange | 5.61 µs | 5.63 µs | 5.64 µs | 5.68 µs | 11.4 µs |
| 20000 | WhileNeeded | 9.72 µs | 9.76 µs | 9.77 µs | 9.81 µs | 10.2 µs |

### reversed

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 10.0 µs | 10.2 µs | 10.2 µs | 10.3 µs | 10.7 µs |
| 100 | UntilNoChange | 10.5 µs | 15.6 µs | 15.8 µs | 16.0 µs | 16.6 µs |
| 100 | WhileNeeded | 9.50 µs | 9.75 µs | 9.76 µs | 9.79 µs | 10.1 µs |
| 1000 | PassPerItem | 993 µs | 997 µs | 998 µs | 1.00 ms | 1.04 ms |
| 1000 | UntilNoChange | 1.49 ms | 1.51 ms | 1.52 ms | 1.53 ms | 1.58 ms |
| 1000 | WhileNeeded | 1.04 ms | 1.08 ms | 1.08 ms | 1.08 ms | 1.11 ms |
| 2000 | PassPerItem | 3.91 ms | 3.95 ms | 3.96 ms | 3.97 ms | 4.21 ms |
| 2000 | UntilNoChange | 5.99 ms | 6.02 ms | 6.03 ms | 6.04 ms | 6.70 ms |
| 2000 | WhileNeeded | 4.22 ms | 4.32 ms | 4.32 ms | 4.34 ms | 4.49 ms |
| 5000 | PassPerItem | 24.4 ms | 24.6 ms | 24.6 ms | 24.7 ms | 27.9 ms |
| 5000 | UntilNoChange | 37.4 ms | 37.4 ms | 37.5 ms | 37.5 ms | 37.9 ms |
| 5000 | WhileNeeded | 26.7 ms | 27.0 ms | 27.0 ms | 27.0 ms | 27.4 ms |
| 10000 | PassPerItem | 101 ms | 101 ms | 102 ms | 102 ms | 110 ms |
| 10000 | UntilNoChange | 109 ms | 110 ms | 110 ms | 111 ms | 117 ms |
| 10000 | WhileNeeded | 108 ms | 109 ms | 109 ms | 109 ms | 112 ms |
| 20000 | PassPerItem | 372 ms | 372 ms | 373 ms | 437 ms | 450 ms |
| 20000 | UntilNoChange | 430 ms | 431 ms | 432 ms | 452 ms | 461 ms |
| 20000 | WhileNeeded | 431 ms | 435 ms | 435 ms | 436 ms | 445 ms |

### nearly sorted (local swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 6.20 µs | 6.21 µs | 6.26 µs | 6.47 µs | 6.69 µs |
| 100 | UntilNoChange | 409 ns | 540 ns | 684 ns | 723 ns | 1.48 µs |
| 100 | WhileNeeded | 198 ns | 370 ns | 433 ns | 717 ns | 857 ns |
| 1000 | PassPerItem | 585 µs | 588 µs | 589 µs | 594 µs | 612 µs |
| 1000 | UntilNoChange | 9.66 µs | 9.77 µs | 10.5 µs | 14.0 µs | 15.7 µs |
| 1000 | WhileNeeded | 8.44 µs | 9.35 µs | 9.59 µs | 11.4 µs | 13.0 µs |
| 2000 | PassPerItem | 2.33 ms | 2.33 ms | 2.34 ms | 2.36 ms | 2.67 ms |
| 2000 | UntilNoChange | 19.7 µs | 21.3 µs | 28.0 µs | 29.9 µs | 36.6 µs |
| 2000 | WhileNeeded | 19.1 µs | 19.7 µs | 21.1 µs | 23.6 µs | 28.5 µs |
| 5000 | PassPerItem | 14.4 ms | 14.5 ms | 14.5 ms | 14.6 ms | 14.9 ms |
| 5000 | UntilNoChange | 50.1 µs | 67.1 µs | 75.0 µs | 87.5 µs | 92.7 µs |
| 5000 | WhileNeeded | 48.3 µs | 63.3 µs | 65.8 µs | 76.1 µs | 84.7 µs |
| 10000 | PassPerItem | 60.4 ms | 62.5 ms | 64.1 ms | 66.4 ms | 87.3 ms |
| 10000 | UntilNoChange | 120 µs | 157 µs | 180 µs | 189 µs | 271 µs |
| 10000 | WhileNeeded | 111 µs | 142 µs | 153 µs | 169 µs | 175 µs |
| 20000 | PassPerItem | 237 ms | 239 ms | 245 ms | 256 ms | 260 ms |
| 20000 | UntilNoChange | 293 µs | 313 µs | 344 µs | 361 µs | 385 µs |
| 20000 | WhileNeeded | 268 µs | 294 µs | 316 µs | 336 µs | 374 µs |

### nearly sorted (random swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 6.43 µs | 6.51 µs | 6.66 µs | 6.70 µs | 6.82 µs |
| 100 | UntilNoChange | 3.55 µs | 4.52 µs | 6.32 µs | 7.60 µs | 9.13 µs |
| 100 | WhileNeeded | 1.92 µs | 2.86 µs | 3.49 µs | 3.67 µs | 4.61 µs |
| 1000 | PassPerItem | 630 µs | 640 µs | 642 µs | 646 µs | 668 µs |
| 1000 | UntilNoChange | 614 µs | 779 µs | 792 µs | 830 µs | 904 µs |
| 1000 | WhileNeeded | 399 µs | 437 µs | 443 µs | 454 µs | 467 µs |
| 2000 | PassPerItem | 2.52 ms | 2.54 ms | 2.55 ms | 2.58 ms | 2.86 ms |
| 2000 | UntilNoChange | 2.83 ms | 3.03 ms | 3.13 ms | 3.21 ms | 3.47 ms |
| 2000 | WhileNeeded | 1.70 ms | 1.74 ms | 1.78 ms | 1.81 ms | 1.88 ms |
| 5000 | PassPerItem | 15.8 ms | 15.9 ms | 15.9 ms | 16.0 ms | 16.2 ms |
| 5000 | UntilNoChange | 20.1 ms | 20.9 ms | 21.3 ms | 21.6 ms | 22.5 ms |
| 5000 | WhileNeeded | 11.3 ms | 11.4 ms | 11.5 ms | 11.5 ms | 11.7 ms |
| 10000 | PassPerItem | 80.3 ms | 81.5 ms | 82.9 ms | 86.8 ms | 92.7 ms |
| 10000 | UntilNoChange | 95.3 ms | 100 ms | 103 ms | 104 ms | 106 ms |
| 10000 | WhileNeeded | 51.6 ms | 52.0 ms | 52.2 ms | 52.3 ms | 53.8 ms |
| 20000 | PassPerItem | 381 ms | 383 ms | 385 ms | 387 ms | 395 ms |
| 20000 | UntilNoChange | 390 ms | 396 ms | 399 ms | 402 ms | 445 ms |
| 20000 | WhileNeeded | 219 ms | 221 ms | 223 ms | 224 ms | 233 ms |

### few unique values

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 8.11 µs | 8.28 µs | 8.39 µs | 8.46 µs | 8.73 µs |
| 100 | UntilNoChange | 8.28 µs | 8.59 µs | 8.95 µs | 9.50 µs | 10.7 µs |
| 100 | WhileNeeded | 5.27 µs | 5.34 µs | 5.39 µs | 5.52 µs | 6.13 µs |
| 1000 | PassPerItem | 965 µs | 982 µs | 986 µs | 991 µs | 1.02 ms |
| 1000 | UntilNoChange | 1.07 ms | 1.09 ms | 1.09 ms | 1.10 ms | 1.12 ms |
| 1000 | WhileNeeded | 642 µs | 649 µs | 654 µs | 659 µs | 686 µs |
| 2000 | PassPerItem | 3.98 ms | 4.03 ms | 4.04 ms | 4.06 ms | 4.16 ms |
| 2000 | UntilNoChange | 4.26 ms | 4.32 ms | 4.33 ms | 4.36 ms | 4.44 ms |
| 2000 | WhileNeeded | 2.71 ms | 2.73 ms | 2.74 ms | 2.75 ms | 2.89 ms |
| 5000 | PassPerItem | 23.2 ms | 23.4 ms | 23.4 ms | 23.5 ms | 23.8 ms |
| 5000 | UntilNoChange | 25.3 ms | 25.5 ms | 25.6 ms | 25.7 ms | 25.8 ms |
| 5000 | WhileNeeded | 15.5 ms | 15.7 ms | 15.7 ms | 15.8 ms | 16.0 ms |
| 10000 | PassPerItem | 88.8 ms | 89.6 ms | 89.8 ms | 90.1 ms | 90.9 ms |
| 10000 | UntilNoChange | 97.1 ms | 97.4 ms | 97.6 ms | 98.0 ms | 98.8 ms |
| 10000 | WhileNeeded | 58.2 ms | 58.4 ms | 58.5 ms | 58.6 ms | 59.0 ms |
| 20000 | PassPerItem | 408 ms | 412 ms | 413 ms | 414 ms | 417 ms |
| 20000 | UntilNoChange | 385 ms | 387 ms | 387 ms | 387 ms | 393 ms |
| 20000 | WhileNeeded | 229 ms | 230 ms | 230 ms | 231 ms | 236 ms |

