### random

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 4.87 µs | 5.05 µs | 5.19 µs | 5.31 µs | 5.45 µs |
| 100 | UntilNoChange | 7.31 µs | 7.53 µs | 7.68 µs | 7.84 µs | 8.19 µs |
| 100 | WhileNeeded | 4.27 µs | 4.39 µs | 4.47 µs | 4.54 µs | 4.72 µs |
| 1000 | PassPerItem | 817 µs | 831 µs | 840 µs | 857 µs | 912 µs |
| 1000 | UntilNoChange | 1.00 ms | 1.03 ms | 1.05 ms | 1.06 ms | 1.12 ms |
| 1000 | WhileNeeded | 616 µs | 632 µs | 638 µs | 648 µs | 693 µs |
| 2000 | PassPerItem | 3.30 ms | 3.37 ms | 3.42 ms | 3.54 ms | 3.65 ms |
| 2000 | UntilNoChange | 3.98 ms | 4.07 ms | 4.18 ms | 4.30 ms | 4.53 ms |
| 2000 | WhileNeeded | 2.38 ms | 2.47 ms | 2.56 ms | 2.60 ms | 2.64 ms |
| 5000 | PassPerItem | 20.2 ms | 20.5 ms | 20.6 ms | 20.6 ms | 21.3 ms |
| 5000 | UntilNoChange | 25.5 ms | 25.6 ms | 25.9 ms | 26.0 ms | 26.5 ms |
| 5000 | WhileNeeded | 15.3 ms | 15.7 ms | 15.8 ms | 15.8 ms | 15.9 ms |
| 10000 | PassPerItem | 93.2 ms | 95.2 ms | 95.7 ms | 96.1 ms | 98.0 ms |
| 10000 | UntilNoChange | 109 ms | 111 ms | 112 ms | 112 ms | 114 ms |
| 10000 | WhileNeeded | 60.7 ms | 61.8 ms | 62.0 ms | 62.2 ms | 64.2 ms |
| 20000 | PassPerItem | 452 ms | 456 ms | 458 ms | 460 ms | 502 ms |
| 20000 | UntilNoChange | 490 ms | 504 ms | 506 ms | 509 ms | 557 ms |
| 20000 | WhileNeeded | 261 ms | 264 ms | 265 ms | 267 ms | 269 ms |

### sorted

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 2.84 µs | 2.90 µs | 2.92 µs | 2.95 µs | 3.36 µs |
| 100 | UntilNoChange | 25.3 ns | 26.1 ns | 26.4 ns | 27.2 ns | 33.9 ns |
| 100 | WhileNeeded | 25.3 ns | 25.8 ns | 26.1 ns | 26.6 ns | 28.7 ns |
| 1000 | PassPerItem | 556 µs | 565 µs | 572 µs | 577 µs | 597 µs |
| 1000 | UntilNoChange | 250 ns | 256 ns | 261 ns | 263 ns | 284 ns |
| 1000 | WhileNeeded | 247 ns | 252 ns | 257 ns | 260 ns | 276 ns |
| 2000 | PassPerItem | 2.19 ms | 2.23 ms | 2.26 ms | 2.29 ms | 2.44 ms |
| 2000 | UntilNoChange | 495 ns | 505 ns | 509 ns | 518 ns | 583 ns |
| 2000 | WhileNeeded | 489 ns | 498 ns | 502 ns | 512 ns | 597 ns |
| 5000 | PassPerItem | 13.7 ms | 14.0 ms | 14.0 ms | 14.1 ms | 15.3 ms |
| 5000 | UntilNoChange | 1.27 µs | 1.29 µs | 1.31 µs | 1.33 µs | 1.40 µs |
| 5000 | WhileNeeded | 1.17 µs | 1.27 µs | 1.28 µs | 1.31 µs | 1.41 µs |
| 10000 | PassPerItem | 62.0 ms | 63.7 ms | 64.2 ms | 64.8 ms | 66.9 ms |
| 10000 | UntilNoChange | 2.82 µs | 2.89 µs | 2.91 µs | 2.97 µs | 3.37 µs |
| 10000 | WhileNeeded | 2.82 µs | 2.88 µs | 2.92 µs | 2.97 µs | 3.42 µs |
| 20000 | PassPerItem | 227 ms | 228 ms | 229 ms | 229 ms | 246 ms |
| 20000 | UntilNoChange | 5.61 µs | 5.76 µs | 5.84 µs | 5.91 µs | 6.31 µs |
| 20000 | WhileNeeded | 5.61 µs | 5.73 µs | 5.78 µs | 5.92 µs | 6.36 µs |

### reversed

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 5.51 µs | 5.63 µs | 5.75 µs | 7.76 µs | 8.16 µs |
| 100 | UntilNoChange | 9.95 µs | 10.3 µs | 10.4 µs | 10.6 µs | 11.1 µs |
| 100 | WhileNeeded | 5.84 µs | 5.97 µs | 6.04 µs | 6.13 µs | 6.48 µs |
| 1000 | PassPerItem | 996 µs | 1.01 ms | 1.03 ms | 1.03 ms | 1.20 ms |
| 1000 | UntilNoChange | 1.51 ms | 1.53 ms | 1.56 ms | 1.56 ms | 1.68 ms |
| 1000 | WhileNeeded | 1.08 ms | 1.09 ms | 1.10 ms | 1.11 ms | 1.13 ms |
| 2000 | PassPerItem | 3.98 ms | 4.04 ms | 4.06 ms | 4.09 ms | 4.37 ms |
| 2000 | UntilNoChange | 6.13 ms | 6.18 ms | 6.23 ms | 6.27 ms | 6.74 ms |
| 2000 | WhileNeeded | 4.27 ms | 4.40 ms | 4.43 ms | 4.48 ms | 4.78 ms |
| 5000 | PassPerItem | 24.5 ms | 25.1 ms | 25.2 ms | 25.3 ms | 25.8 ms |
| 5000 | UntilNoChange | 38.0 ms | 38.4 ms | 38.5 ms | 38.7 ms | 39.5 ms |
| 5000 | WhileNeeded | 27.3 ms | 27.7 ms | 27.7 ms | 27.9 ms | 29.4 ms |
| 10000 | PassPerItem | 103 ms | 104 ms | 104 ms | 104 ms | 107 ms |
| 10000 | UntilNoChange | 111 ms | 112 ms | 113 ms | 113 ms | 115 ms |
| 10000 | WhileNeeded | 110 ms | 111 ms | 112 ms | 112 ms | 114 ms |
| 20000 | PassPerItem | 381 ms | 383 ms | 383 ms | 384 ms | 449 ms |
| 20000 | UntilNoChange | 439 ms | 441 ms | 442 ms | 444 ms | 465 ms |
| 20000 | WhileNeeded | 443 ms | 444 ms | 445 ms | 446 ms | 450 ms |

### nearly sorted (local swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 3.78 µs | 3.84 µs | 3.88 µs | 3.93 µs | 4.03 µs |
| 100 | UntilNoChange | 678 ns | 708 ns | 798 ns | 1.33 µs | 1.64 µs |
| 100 | WhileNeeded | 489 ns | 502 ns | 511 ns | 592 ns | 622 ns |
| 1000 | PassPerItem | 587 µs | 600 µs | 605 µs | 611 µs | 627 µs |
| 1000 | UntilNoChange | 8.23 µs | 8.45 µs | 8.56 µs | 12.0 µs | 12.6 µs |
| 1000 | WhileNeeded | 6.78 µs | 7.05 µs | 7.23 µs | 8.70 µs | 9.12 µs |
| 2000 | PassPerItem | 2.34 ms | 2.39 ms | 2.41 ms | 2.43 ms | 2.49 ms |
| 2000 | UntilNoChange | 16.8 µs | 17.8 µs | 18.7 µs | 25.5 µs | 26.7 µs |
| 2000 | WhileNeeded | 14.7 µs | 15.1 µs | 15.3 µs | 21.4 µs | 22.3 µs |
| 5000 | PassPerItem | 14.6 ms | 14.9 ms | 14.9 ms | 15.0 ms | 15.3 ms |
| 5000 | UntilNoChange | 43.2 µs | 44.8 µs | 64.4 µs | 71.8 µs | 76.3 µs |
| 5000 | WhileNeeded | 37.8 µs | 39.1 µs | 51.2 µs | 63.0 µs | 66.7 µs |
| 10000 | PassPerItem | 64.2 ms | 65.5 ms | 66.2 ms | 67.3 ms | 77.1 ms |
| 10000 | UntilNoChange | 125 µs | 130 µs | 146 µs | 149 µs | 157 µs |
| 10000 | WhileNeeded | 113 µs | 117 µs | 118 µs | 121 µs | 126 µs |
| 20000 | PassPerItem | 242 ms | 244 ms | 245 ms | 246 ms | 257 ms |
| 20000 | UntilNoChange | 287 µs | 299 µs | 311 µs | 320 µs | 335 µs |
| 20000 | WhileNeeded | 231 µs | 241 µs | 248 µs | 258 µs | 275 µs |

### nearly sorted (random swaps)

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 3.82 µs | 3.90 µs | 3.93 µs | 3.97 µs | 4.16 µs |
| 100 | UntilNoChange | 3.45 µs | 3.56 µs | 5.08 µs | 7.23 µs | 7.44 µs |
| 100 | WhileNeeded | 2.13 µs | 2.21 µs | 2.61 µs | 3.21 µs | 3.42 µs |
| 1000 | PassPerItem | 638 µs | 656 µs | 660 µs | 669 µs | 707 µs |
| 1000 | UntilNoChange | 786 µs | 809 µs | 861 µs | 884 µs | 923 µs |
| 1000 | WhileNeeded | 317 µs | 325 µs | 331 µs | 335 µs | 347 µs |
| 2000 | PassPerItem | 2.55 ms | 2.60 ms | 2.63 ms | 2.66 ms | 2.96 ms |
| 2000 | UntilNoChange | 2.86 ms | 2.95 ms | 3.29 ms | 3.42 ms | 3.49 ms |
| 2000 | WhileNeeded | 1.73 ms | 1.78 ms | 1.83 ms | 1.85 ms | 1.92 ms |
| 5000 | PassPerItem | 15.8 ms | 16.3 ms | 16.4 ms | 16.4 ms | 17.1 ms |
| 5000 | UntilNoChange | 20.4 ms | 20.7 ms | 21.8 ms | 21.9 ms | 22.8 ms |
| 5000 | WhileNeeded | 11.5 ms | 11.6 ms | 11.7 ms | 11.7 ms | 11.9 ms |
| 10000 | PassPerItem | 81.8 ms | 83.3 ms | 83.8 ms | 85.0 ms | 89.1 ms |
| 10000 | UntilNoChange | 98.8 ms | 100 ms | 104 ms | 106 ms | 108 ms |
| 10000 | WhileNeeded | 52.4 ms | 53.2 ms | 53.5 ms | 53.6 ms | 56.4 ms |
| 20000 | PassPerItem | 390 ms | 393 ms | 395 ms | 399 ms | 402 ms |
| 20000 | UntilNoChange | 408 ms | 410 ms | 416 ms | 429 ms | 434 ms |
| 20000 | WhileNeeded | 226 ms | 228 ms | 231 ms | 239 ms | 241 ms |

### few unique values

| n | algorithm | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| 100 | PassPerItem | 4.65 µs | 4.81 µs | 4.89 µs | 4.95 µs | 5.17 µs |
| 100 | UntilNoChange | 6.06 µs | 6.41 µs | 6.60 µs | 6.74 µs | 7.01 µs |
| 100 | WhileNeeded | 3.75 µs | 3.89 µs | 3.95 µs | 4.02 µs | 4.19 µs |
| 1000 | PassPerItem | 988 µs | 1.03 ms | 1.05 ms | 1.08 ms | 1.17 ms |
| 1000 | UntilNoChange | 1.10 ms | 1.15 ms | 1.16 ms | 1.20 ms | 2.08 ms |
| 1000 | WhileNeeded | 632 µs | 661 µs | 678 µs | 696 µs | 787 µs |
| 2000 | PassPerItem | 4.05 ms | 4.14 ms | 4.16 ms | 4.19 ms | 4.26 ms |
| 2000 | UntilNoChange | 4.38 ms | 4.44 ms | 4.47 ms | 4.52 ms | 4.62 ms |
| 2000 | WhileNeeded | 2.75 ms | 2.82 ms | 2.84 ms | 2.86 ms | 2.98 ms |
| 5000 | PassPerItem | 23.3 ms | 23.8 ms | 23.9 ms | 24.1 ms | 24.3 ms |
| 5000 | UntilNoChange | 25.7 ms | 26.1 ms | 26.2 ms | 26.2 ms | 26.4 ms |
| 5000 | WhileNeeded | 15.7 ms | 16.0 ms | 16.1 ms | 16.2 ms | 16.8 ms |
| 10000 | PassPerItem | 90.5 ms | 91.5 ms | 92.0 ms | 92.4 ms | 95.0 ms |
| 10000 | UntilNoChange | 99.2 ms | 100 ms | 100 ms | 101 ms | 102 ms |
| 10000 | WhileNeeded | 58.9 ms | 59.8 ms | 60.0 ms | 60.1 ms | 61.6 ms |
| 20000 | PassPerItem | 416 ms | 423 ms | 425 ms | 430 ms | 435 ms |
| 20000 | UntilNoChange | 418 ms | 420 ms | 422 ms | 423 ms | 426 ms |
| 20000 | WhileNeeded | 233 ms | 234 ms | 235 ms | 236 ms | 242 ms |

