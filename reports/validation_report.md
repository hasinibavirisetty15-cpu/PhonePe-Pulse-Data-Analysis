# Data validation report

Method: each check tests one rule on a number of units (rows, state-quarters or tables). There is no external ground truth, so this measures internal consistency, not accuracy against the real world.

- Checks run: **22** (merged-table checks included: yes)
- Checks fully passed: **19 of 22 (86.4%)**
- Overall unit pass rate: **99.972%** (250,204 of 250,273 units)
- Target of 80%: **MET** (both measures must be at least 80%)

| Group | Check | Tested | Passed | Pass rate | Status | Note |
|---|---|---:|---:|---:|---|---|
| Schema | Expected columns present in every table | 6 | 6 | 100.00% | PASS |  |
| Schema | Expected data types in every table | 6 | 6 | 100.00% | PASS |  |
| Row quality | No missing values | 51,442 | 51,442 | 100.00% | PASS |  |
| Row quality | No duplicate rows on the natural key | 51,442 | 51,442 | 100.00% | PASS |  |
| Row quality | Valid ranges (year 2018-2022, quarter 1-4, counts and amounts > 0) | 51,442 | 51,442 | 100.00% | PASS |  |
| Coverage | Same 36 states in every table | 6 | 6 | 100.00% | PASS |  |
| Coverage | All 20 quarters (2018 Q1 - 2022 Q4) present | 6 | 5 | 83.33% | WARN | aggregated_user covers only 17 of 20 quarters (ends 2022 Q1) - brand charts stop there |
| Reconciliation | aggregated_transaction = sum of map_transaction (counts and amount, per state-quarter) | 720 | 656 | 91.11% | FAIL |  |
| Reconciliation | aggregated_user total = sum of map_user (per state-quarter, overlapping quarters) | 612 | 612 | 100.00% | PASS |  |
| Reconciliation | Brand shares add up to 100% (per state-quarter) | 612 | 612 | 100.00% | PASS |  |
| Reconciliation | top_transaction rows match map_transaction (same counts and amount) | 5,920 | 5,920 | 100.00% | PASS | Delhi's 'central delhi' (top tables) and 'central district' (map tables) are unified by an alias |
| Reconciliation | top_user rows match map_user (same registered users) | 5,920 | 5,920 | 100.00% | PASS |  |
| Reconciliation | Every map_user row also exists in map_transaction | 14,640 | 14,636 | 99.97% | WARN | 4 Arunachal Pradesh rows (Anjaw 2018 Q1; Shi Yomi 2018 Q1-Q3) have users but no transactions |
| Logic | Registered users never fall from one quarter to the next (running total) | 684 | 684 | 100.00% | PASS |  |
| Logic | Top lists hold at most 10 rows per state-quarter | 720 | 720 | 100.00% | PASS |  |
| Merged table | master_long has one row for every source row | 1 | 1 | 100.00% | PASS |  |
| Merged table | master_long has the required columns | 1 | 1 | 100.00% | PASS |  |
| Merged table | No missing key fields in master_long (source_table, state, region, year, quarter) | 51,442 | 51,442 | 100.00% | PASS |  |
| Merged table | Counts and amounts in master_long equal the original files (3 tables x 2 measures) | 6 | 6 | 100.00% | PASS |  |
| Merged table | master_district_quarter has no duplicate district-quarter rows | 14,640 | 14,640 | 100.00% | PASS |  |
| Merged table | master_district_quarter totals equal the original files (counts, amount, users) | 3 | 3 | 100.00% | PASS |  |
| Merged table | All top_transaction and top_user rows were matched into master_district_quarter | 2 | 2 | 100.00% | PASS |  |

WARN = known data limitation, explained in the note. FAIL = a rule that must hold but does not.