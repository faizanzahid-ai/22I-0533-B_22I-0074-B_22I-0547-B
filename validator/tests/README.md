# Validator test workbooks

Made by `python validator/make_tests.py cases.xlsx`. Each file holds one case cut from cases.xlsx; broken copies carry exactly one defect.
Run `python validator/validate.py <file> --subset`.

| file | defect |
|---|---|
| valid_39-00.xlsx | valid tier-S Delta Flood case (must PASS) |
| broken_39-00_01_header_renamed.xlsx | V1: crates header 'weight' renamed to 'kg' |
| broken_39-00_02_weight_out_of_range.xlsx | V2: crate 1 weighs 25 kg (range 1..20) |
| broken_39-00_03_repeated_road.xlsx | V3: road 1 repeats the pair of road 0 |
| broken_39-00_04_disconnected.xlsx | V4: an extra location with no road (network not connected) |
| broken_39-00_05_pattern_count.xlsx | V5: count of pattern 1 is off by one |
| broken_39-00_06_wrong_claim.xlsx | V5: cargo_opt claim raised by 5 |
| broken_39-00_07_tour_length.xlsx | V6: tour_length does not match the planted tour |
| broken_39-00_08_signature_food_water.xlsx | V7: Delta Flood with no food/water crates |
| broken_39-00_09_wrong_tier.xlsx | V1: case 00 labelled tier M |
| valid_39-01.xlsx | valid tier-S Mountain Earthquake case (must PASS) |
| broken_39-01_01_waves_overlap.xlsx | V4: a road closed in wave 1 and again in wave 2 |
| broken_39-01_02_edit_bound.xlsx | V5: edit_bound 0 is below the true edit distance |
| broken_39-01_03_rations_sum.xlsx | V6: planted ration selection no longer sums to the target |
| broken_39-01_04_cover_missing_node.xlsx | V6: a node removed from the planted sensor cover |
| broken_39-01_05_assignment.xlsx | V6: every planted switch flipped (rules broken) |
| broken_39-01_06_tick_decreasing.xlsx | V2: the last alarm's tick goes back to 0 |
| broken_39-01_07_degree_too_high.xlsx | V7: Mountain Earthquake with average degree above 2.6 |
| broken_39-01_08_missing_sheet.xlsx | V1: sheet drum_prices missing |
| broken_39-01_09_bad_symbol.xlsx | V2: lower-case 'a' in the radio log |
| valid_39-47.xlsx | valid Best-looking-crate trap case (must PASS) |
| broken_39-47_01_trap_defused.xlsx | V8: capacity 21 lets greedy reach the optimum |
