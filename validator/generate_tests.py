"""
Generate broken test cases for LIFELINE validator.
Requires at least two valid cases, each broken in at least five different ways.
Saves them into validator/tests/.
"""

import os
import sys
import copy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import openpyxl
from generator.generate import LifelineDataGenerator

def save_case_to_workbook(cases_data, output_path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    sheet_definitions = [
        ('cases', [
            'case_id', 'group_seed', 'case_no', 'tier', 'scenario', 'capacity',
            'target_0', 'target_1', 'target_2', 'edit_bound', 'tour_length',
            'sensor_nodes', 'sensor_k', 'safety_vars', 'rations_target'
        ]),
        ('crates', ['case_id', 'crate_id', 'cat', 'weight', 'value', 'expiry', 'serial']),
        ('locations', ['case_id', 'loc_id', 'type', 'penalty']),
        ('roads', ['case_id', 'road_no', 'u', 'v', 'minutes', 'cable']),
        ('waves', ['case_id', 'wave_no', 'road_no']),
        ('radio_log', ['case_id', 'part', 'text']),
        ('radio_patterns', ['case_id', 'pattern_no', 'pattern', 'count']),
        ('radio_reports', ['case_id', 'report_a', 'report_b']),
        ('windows', ['case_id', 'window_id', 'start', 'finish', 'value']),
        ('incidents', ['case_id', 'alarm_id', 'tick', 'priority']),
        ('sites', ['case_id', 'site_no', 'x', 'y']),
        ('tour', ['case_id', 'step', 'site_no']),
        ('pipeline_dims', ['case_id', 'idx', 'dim']),
        ('drum_prices', ['case_id', 'length', 'price']),
        ('sensor_edges', ['case_id', 'u', 'v']),
        ('sensor_cover', ['case_id', 'node']),
        ('safety_rules', ['case_id', 'rule_no', 'lit_1', 'lit_2', 'lit_3']),
        ('safety_planted', ['case_id', 'switch', 'value']),
        ('rations', ['case_id', 'item', 'value', 'planted']),
        ('claims', ['case_id', 'cargo_opt', 'window_count_opt', 'window_value_opt', 'drum_opt', 'tour_opt', 'cover_min'])
    ]

    for sname, cols in sheet_definitions:
        ws = wb.create_sheet(title=sname)
        ws.append(cols)
        rows = cases_data.get(sname, [])
        col2 = cols[1]
        sorted_rows = sorted(rows, key=lambda r: (r['case_id'], r[col2]))
        for r in sorted_rows:
            ws.append([r[c] for c in cols])

    wb.save(output_path)


def generate_broken_tests(tests_dir="validator/tests", base_seed=17):
    os.makedirs(tests_dir, exist_ok=True)

    # Generate master data for 50 cases
    gen = LifelineDataGenerator(base_seed)
    gen.generate_all()

    # We will create broken versions of the workbook targeting Case 00 (Case A) and Case 01 (Case B)
    # Case A: 5 different breakages
    # 1. Broken V1: missing 'claims' sheet
    d1 = copy.deepcopy(gen.cases_data)
    wb1 = openpyxl.Workbook()
    wb1.remove(wb1.active)
    for sname in gen.cases_data.keys():
        if sname == 'claims':
            continue # drop sheet
        ws = wb1.create_sheet(title=sname)
        cols = list(gen.cases_data[sname][0].keys()) if gen.cases_data[sname] else ['case_id']
        ws.append(cols)
        for r in gen.cases_data[sname]:
            ws.append([r[c] for c in cols])
    wb1.save(os.path.join(tests_dir, "caseA_broken_V1_missing_sheet.xlsx"))

    # 2. Broken V2: crate weight out of range (weight = 99 kg > 20 kg) in Case 00
    d2 = copy.deepcopy(gen.cases_data)
    for c in d2['crates']:
        if c['case_id'] == f"{base_seed}-00" and c['crate_id'] == 1:
            c['weight'] = 99
            break
    save_case_to_workbook(d2, os.path.join(tests_dir, "caseA_broken_V2_crate_weight.xlsx"))

    # 3. Broken V3: invalid target reference in Case 00 (target_0 = 9999)
    d3 = copy.deepcopy(gen.cases_data)
    for c in d3['cases']:
        if c['case_id'] == f"{base_seed}-00":
            c['target_0'] = 9999
            break
    save_case_to_workbook(d3, os.path.join(tests_dir, "caseA_broken_V3_invalid_target.xlsx"))

    # 4. Broken V4: disconnected network in Case 00 (remove all edges incident to node 1)
    d4 = copy.deepcopy(gen.cases_data)
    d4['roads'] = [r for r in d4['roads'] if not (r['case_id'] == f"{base_seed}-00" and (r['u'] == 1 or r['v'] == 1))]
    save_case_to_workbook(d4, os.path.join(tests_dir, "caseA_broken_V4_disconnected_network.xlsx"))

    # 5. Broken V5: corrupted claim cargo_opt in Case 00 (cargo_opt = 99999)
    d5 = copy.deepcopy(gen.cases_data)
    for cl in d5['claims']:
        if cl['case_id'] == f"{base_seed}-00":
            cl['cargo_opt'] = 99999
            break
    save_case_to_workbook(d5, os.path.join(tests_dir, "caseA_broken_V5_corrupted_claim.xlsx"))

    # Case B: 5 different breakages
    # 6. Broken V2: invalid location penalty (penalty = 5 not in {0, 1, 2, 4, 6}) in Case 01
    d6 = copy.deepcopy(gen.cases_data)
    for loc in d6['locations']:
        if loc['case_id'] == f"{base_seed}-01" and loc['loc_id'] == 1:
            loc['penalty'] = 5
            break
    save_case_to_workbook(d6, os.path.join(tests_dir, "caseB_broken_V2_invalid_penalty.xlsx"))

    # 7. Broken V3: non-consecutive crate_id in Case 01 (skip crate_id 2)
    d7 = copy.deepcopy(gen.cases_data)
    for c in d7['crates']:
        if c['case_id'] == f"{base_seed}-01" and c['crate_id'] == 2:
            c['crate_id'] = 99
            break
    save_case_to_workbook(d7, os.path.join(tests_dir, "caseB_broken_V3_nonconsecutive_crate_id.xlsx"))

    # 8. Broken V4: road appears in multiple waves in Case 01
    d8 = copy.deepcopy(gen.cases_data)
    target_waves = [w for w in d8['waves'] if w['case_id'] == f"{base_seed}-01"]
    if len(target_waves) >= 2:
        target_waves[1]['road_no'] = target_waves[0]['road_no']
    save_case_to_workbook(d8, os.path.join(tests_dir, "caseB_broken_V4_overlapping_waves.xlsx"))

    # 9. Broken V6: planted vertex cover does not cover edge in Case 01
    d9 = copy.deepcopy(gen.cases_data)
    # Remove all cover nodes except one
    d9['sensor_cover'] = [sc for sc in d9['sensor_cover'] if sc['case_id'] != f"{base_seed}-01"]
    d9['sensor_cover'].append({'case_id': f"{base_seed}-01", 'node': 0})
    for cs in d9['cases']:
        if cs['case_id'] == f"{base_seed}-01":
            cs['sensor_k'] = 1
            break
    save_case_to_workbook(d9, os.path.join(tests_dir, "caseB_broken_V6_invalid_vertex_cover.xlsx"))

    # 10. Broken V7: violates signature rule of Study 2 (case 01 is Study 2: mean alarm priority < 6.0)
    d10 = copy.deepcopy(gen.cases_data)
    for inc in d10['incidents']:
        if inc['case_id'] == f"{base_seed}-01":
            inc['priority'] = 1 # all priority 1 -> mean priority 1.0 < 6.0
    save_case_to_workbook(d10, os.path.join(tests_dir, "caseB_broken_V7_signature_priority.xlsx"))

    print(f"Generated 10 broken test cases successfully in {tests_dir}!")

if __name__ == "__main__":
    generate_broken_tests()
