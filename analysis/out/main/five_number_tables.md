### random

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 7.76 µs | 7.88 µs | 7.99 µs | 8.06 µs | 8.52 µs |
| 100 | UntilNoChange | 8.64 µs | 9.19 µs | 9.63 µs | 9.83 µs | 10.4 µs |
| 100 | WhileNeeded | 5.40 µs | 5.53 µs | 5.77 µs | 5.87 µs | 6.32 µs |
| 1000 | PassPerItem | 798 µs | 812 µs | 816 µs | 819 µs | 866 µs |
| 1000 | UntilNoChange | 980 µs | 1.00 ms | 1.02 ms | 1.03 ms | 1.11 ms |
| 1000 | WhileNeeded | 592 µs | 609 µs | 615 µs | 620 µs | 665 µs |
| 2000 | PassPerItem | 3.24 ms | 3.27 ms | 3.28 ms | 3.32 ms | 3.58 ms |
| 2000 | UntilNoChange | 3.90 ms | 4.03 ms | 4.09 ms | 4.12 ms | 4.28 ms |
| 2000 | WhileNeeded | 2.33 ms | 2.46 ms | 2.48 ms | 2.50 ms | 2.59 ms |
| 5000 | PassPerItem | 20.0 ms | 20.1 ms | 20.1 ms | 20.3 ms | 21.3 ms |
| 5000 | UntilNoChange | 24.6 ms | 25.1 ms | 25.3 ms | 25.5 ms | 26.7 ms |
| 5000 | WhileNeeded | 15.2 ms | 15.3 ms | 15.3 ms | 15.4 ms | 15.6 ms |
| 10000 | PassPerItem | 91.7 ms | 93.1 ms | 94.0 ms | 95.6 ms | 102 ms |
| 10000 | UntilNoChange | 106 ms | 108 ms | 109 ms | 110 ms | 113 ms |
| 10000 | WhileNeeded | 58.9 ms | 60.8 ms | 61.1 ms | 61.4 ms | 63.9 ms |
| 20000 | PassPerItem | 444 ms | 449 ms | 451 ms | 454 ms | 523 ms |
| 20000 | UntilNoChange | 483 ms | 490 ms | 492 ms | 493 ms | 504 ms |
| 20000 | WhileNeeded | 255 ms | 257 ms | 258 ms | 260 ms | 284 ms |

### sorted

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 4.89 µs | 5.44 µs | 5.46 µs | 5.54 µs | 5.68 µs |
| 100 | UntilNoChange | 25.5 ns | 25.8 ns | 26.2 ns | 26.8 ns | 74.6 ns |
| 100 | WhileNeeded | 24.9 ns | 25.2 ns | 25.5 ns | 25.7 ns | 66.8 ns |
| 1000 | PassPerItem | 543 µs | 552 µs | 553 µs | 555 µs | 642 µs |
| 1000 | UntilNoChange | 250 ns | 256 ns | 570 ns | 575 ns | 624 ns |
| 1000 | WhileNeeded | 264 ns | 273 ns | 493 ns | 495 ns | 531 ns |
| 2000 | PassPerItem | 2.10 ms | 2.19 ms | 2.20 ms | 2.21 ms | 2.40 ms |
| 2000 | UntilNoChange | 1.05 µs | 1.12 µs | 1.13 µs | 1.14 µs | 1.21 µs |
| 2000 | WhileNeeded | 924 ns | 964 ns | 975 ns | 981 ns | 1.02 µs |
| 5000 | PassPerItem | 13.6 ms | 13.6 ms | 13.6 ms | 13.7 ms | 14.8 ms |
| 5000 | UntilNoChange | 2.80 µs | 2.82 µs | 2.82 µs | 2.85 µs | 3.09 µs |
| 5000 | WhileNeeded | 2.30 µs | 2.41 µs | 2.42 µs | 2.43 µs | 2.58 µs |
| 10000 | PassPerItem | 58.2 ms | 63.4 ms | 64.6 ms | 65.6 ms | 94.8 ms |
| 10000 | UntilNoChange | 5.46 µs | 5.71 µs | 5.72 µs | 5.75 µs | 6.08 µs |
| 10000 | WhileNeeded | 4.87 µs | 4.90 µs | 4.92 µs | 4.96 µs | 5.31 µs |
| 20000 | PassPerItem | 223 ms | 223 ms | 223 ms | 224 ms | 237 ms |
| 20000 | UntilNoChange | 5.60 µs | 5.64 µs | 5.74 µs | 11.5 µs | 11.8 µs |
| 20000 | WhileNeeded | 9.47 µs | 9.76 µs | 9.79 µs | 9.86 µs | 10.3 µs |

### reversed

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 9.95 µs | 10.2 µs | 10.3 µs | 10.4 µs | 10.9 µs |
| 100 | UntilNoChange | 10.5 µs | 15.6 µs | 15.8 µs | 15.9 µs | 16.7 µs |
| 100 | WhileNeeded | 9.11 µs | 9.75 µs | 9.76 µs | 9.79 µs | 10.1 µs |
| 1000 | PassPerItem | 986 µs | 997 µs | 998 µs | 1.00 ms | 1.11 ms |
| 1000 | UntilNoChange | 1.44 ms | 1.51 ms | 1.51 ms | 1.53 ms | 1.63 ms |
| 1000 | WhileNeeded | 1.03 ms | 1.08 ms | 1.08 ms | 1.08 ms | 1.14 ms |
| 2000 | PassPerItem | 3.88 ms | 3.95 ms | 3.96 ms | 3.97 ms | 5.30 ms |
| 2000 | UntilNoChange | 5.97 ms | 6.02 ms | 6.02 ms | 6.04 ms | 6.91 ms |
| 2000 | WhileNeeded | 4.22 ms | 4.32 ms | 4.32 ms | 4.33 ms | 4.64 ms |
| 5000 | PassPerItem | 24.4 ms | 24.6 ms | 24.6 ms | 24.8 ms | 27.9 ms |
| 5000 | UntilNoChange | 37.0 ms | 37.5 ms | 37.5 ms | 37.6 ms | 41.6 ms |
| 5000 | WhileNeeded | 26.6 ms | 27.0 ms | 27.0 ms | 27.0 ms | 27.4 ms |
| 10000 | PassPerItem | 101 ms | 102 ms | 102 ms | 104 ms | 116 ms |
| 10000 | UntilNoChange | 109 ms | 110 ms | 110 ms | 113 ms | 120 ms |
| 10000 | WhileNeeded | 108 ms | 109 ms | 109 ms | 109 ms | 116 ms |
| 20000 | PassPerItem | 372 ms | 372 ms | 373 ms | 437 ms | 450 ms |
| 20000 | UntilNoChange | 430 ms | 431 ms | 432 ms | 452 ms | 475 ms |
| 20000 | WhileNeeded | 431 ms | 435 ms | 435 ms | 436 ms | 446 ms |

### nearly sorted (local swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 6.19 µs | 6.21 µs | 6.27 µs | 6.47 µs | 6.69 µs |
| 100 | UntilNoChange | 409 ns | 545 ns | 713 ns | 865 ns | 1.53 µs |
| 100 | WhileNeeded | 198 ns | 373 ns | 444 ns | 690 ns | 867 ns |
| 1000 | PassPerItem | 576 µs | 588 µs | 590 µs | 592 µs | 648 µs |
| 1000 | UntilNoChange | 9.63 µs | 9.78 µs | 10.7 µs | 14.1 µs | 15.7 µs |
| 1000 | WhileNeeded | 8.40 µs | 9.35 µs | 9.59 µs | 11.4 µs | 13.2 µs |
| 2000 | PassPerItem | 2.28 ms | 2.33 ms | 2.34 ms | 2.36 ms | 2.67 ms |
| 2000 | UntilNoChange | 19.3 µs | 21.3 µs | 27.9 µs | 29.9 µs | 37.8 µs |
| 2000 | WhileNeeded | 18.9 µs | 19.7 µs | 21.1 µs | 23.6 µs | 28.5 µs |
| 5000 | PassPerItem | 14.4 ms | 14.5 ms | 14.6 ms | 14.7 ms | 16.7 ms |
| 5000 | UntilNoChange | 50.0 µs | 67.2 µs | 74.9 µs | 87.4 µs | 92.7 µs |
| 5000 | WhileNeeded | 48.3 µs | 63.3 µs | 66.2 µs | 76.1 µs | 87.7 µs |
| 10000 | PassPerItem | 60.4 ms | 62.7 ms | 64.1 ms | 65.9 ms | 87.6 ms |
| 10000 | UntilNoChange | 120 µs | 157 µs | 186 µs | 191 µs | 273 µs |
| 10000 | WhileNeeded | 111 µs | 142 µs | 153 µs | 169 µs | 185 µs |
| 20000 | PassPerItem | 237 ms | 239 ms | 248 ms | 256 ms | 270 ms |
| 20000 | UntilNoChange | 292 µs | 312 µs | 344 µs | 362 µs | 391 µs |
| 20000 | WhileNeeded | 268 µs | 295 µs | 319 µs | 336 µs | 382 µs |

### nearly sorted (random swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 6.42 µs | 6.56 µs | 6.67 µs | 6.76 µs | 7.29 µs |
| 100 | UntilNoChange | 3.54 µs | 4.52 µs | 6.37 µs | 7.51 µs | 9.39 µs |
| 100 | WhileNeeded | 1.92 µs | 2.84 µs | 3.48 µs | 3.65 µs | 4.61 µs |
| 1000 | PassPerItem | 622 µs | 639 µs | 642 µs | 645 µs | 699 µs |
| 1000 | UntilNoChange | 614 µs | 779 µs | 789 µs | 832 µs | 904 µs |
| 1000 | WhileNeeded | 399 µs | 436 µs | 442 µs | 453 µs | 470 µs |
| 2000 | PassPerItem | 2.51 ms | 2.54 ms | 2.56 ms | 2.57 ms | 2.86 ms |
| 2000 | UntilNoChange | 2.81 ms | 3.03 ms | 3.13 ms | 3.21 ms | 3.47 ms |
| 2000 | WhileNeeded | 1.68 ms | 1.74 ms | 1.78 ms | 1.81 ms | 1.90 ms |
| 5000 | PassPerItem | 15.8 ms | 15.9 ms | 16.0 ms | 16.1 ms | 17.9 ms |
| 5000 | UntilNoChange | 20.1 ms | 20.9 ms | 21.3 ms | 21.6 ms | 22.6 ms |
| 5000 | WhileNeeded | 11.2 ms | 11.4 ms | 11.5 ms | 11.6 ms | 13.5 ms |
| 10000 | PassPerItem | 80.3 ms | 81.5 ms | 82.7 ms | 86.7 ms | 101 ms |
| 10000 | UntilNoChange | 95.3 ms | 101 ms | 103 ms | 104 ms | 107 ms |
| 10000 | WhileNeeded | 51.5 ms | 52.1 ms | 52.3 ms | 52.7 ms | 55.9 ms |
| 20000 | PassPerItem | 381 ms | 384 ms | 385 ms | 387 ms | 395 ms |
| 20000 | UntilNoChange | 389 ms | 396 ms | 400 ms | 402 ms | 475 ms |
| 20000 | WhileNeeded | 219 ms | 221 ms | 223 ms | 224 ms | 234 ms |

### few unique values

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 7.94 µs | 8.30 µs | 8.40 µs | 8.47 µs | 8.84 µs |
| 100 | UntilNoChange | 8.28 µs | 8.58 µs | 8.95 µs | 9.51 µs | 10.8 µs |
| 100 | WhileNeeded | 5.21 µs | 5.35 µs | 5.43 µs | 5.55 µs | 6.13 µs |
| 1000 | PassPerItem | 965 µs | 986 µs | 992 µs | 1.00 ms | 1.12 ms |
| 1000 | UntilNoChange | 1.07 ms | 1.09 ms | 1.10 ms | 1.12 ms | 1.25 ms |
| 1000 | WhileNeeded | 642 µs | 654 µs | 660 µs | 670 µs | 782 µs |
| 2000 | PassPerItem | 3.98 ms | 4.03 ms | 4.05 ms | 4.07 ms | 4.17 ms |
| 2000 | UntilNoChange | 4.26 ms | 4.32 ms | 4.34 ms | 4.37 ms | 4.52 ms |
| 2000 | WhileNeeded | 2.71 ms | 2.74 ms | 2.75 ms | 2.78 ms | 2.98 ms |
| 5000 | PassPerItem | 23.1 ms | 23.3 ms | 23.4 ms | 23.5 ms | 24.1 ms |
| 5000 | UntilNoChange | 25.2 ms | 25.4 ms | 25.6 ms | 25.6 ms | 26.2 ms |
| 5000 | WhileNeeded | 15.5 ms | 15.7 ms | 15.7 ms | 15.8 ms | 16.0 ms |
| 10000 | PassPerItem | 88.8 ms | 89.6 ms | 89.8 ms | 90.1 ms | 94.7 ms |
| 10000 | UntilNoChange | 96.8 ms | 97.4 ms | 97.6 ms | 98.1 ms | 99.0 ms |
| 10000 | WhileNeeded | 58.2 ms | 58.4 ms | 58.5 ms | 58.6 ms | 59.3 ms |
| 20000 | PassPerItem | 408 ms | 412 ms | 413 ms | 414 ms | 417 ms |
| 20000 | UntilNoChange | 384 ms | 387 ms | 387 ms | 387 ms | 393 ms |
| 20000 | WhileNeeded | 229 ms | 230 ms | 230 ms | 231 ms | 238 ms |

