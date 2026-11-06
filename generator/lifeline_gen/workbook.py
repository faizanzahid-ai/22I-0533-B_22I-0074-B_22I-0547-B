"""Write cases.xlsx: 20 sheets in the order of Section 3, header in row 1, no formulas."""
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

SHEETS = [
    ("cases", ["case_id", "group_seed", "case_no", "tier", "scenario", "capacity", "target_0",
               "target_1", "target_2", "edit_bound", "tour_length", "sensor_nodes", "sensor_k",
               "safety_vars", "rations_target"]),
    ("crates", ["case_id", "crate_id", "cat", "weight", "value", "expiry", "serial"]),
    ("locations", ["case_id", "loc_id", "type", "penalty"]),
    ("roads", ["case_id", "road_no", "u", "v", "minutes", "cable"]),
    ("waves", ["case_id", "wave_no", "road_no"]),
    ("radio_log", ["case_id", "part", "text"]),
    ("radio_patterns", ["case_id", "pattern_no", "pattern", "count"]),
    ("radio_reports", ["case_id", "report_a", "report_b"]),
    ("windows", ["case_id", "window_id", "start", "finish", "value"]),
    ("incidents", ["case_id", "alarm_id", "tick", "priority"]),
    ("sites", ["case_id", "site_no", "x", "y"]),
    ("tour", ["case_id", "step", "site_no"]),
    ("pipeline_dims", ["case_id", "idx", "dim"]),
    ("drum_prices", ["case_id", "length", "price"]),
    ("sensor_edges", ["case_id", "u", "v"]),
    ("sensor_cover", ["case_id", "node"]),
    ("safety_rules", ["case_id", "rule_no", "lit_1", "lit_2", "lit_3"]),
    ("safety_planted", ["case_id", "switch", "value"]),
    ("rations", ["case_id", "item", "value", "planted"]),
    ("claims", ["case_id", "cargo_opt", "window_count_opt", "window_value_opt", "drum_opt",
                "tour_opt", "cover_min"]),
]


def write_workbook(path, rows_by_sheet):
    """rows_by_sheet[name] = list of row tuples (already sorted)."""
    wb = Workbook(write_only=True)
    for name, header in SHEETS:
        ws = wb.create_sheet(name)
        ws.append(header)
        for row in rows_by_sheet[name]:
            out = []
            for val in row:
                if isinstance(val, str):
                    c = WriteOnlyCell(ws, value=val)
                    c.number_format = "@"          # store text cells as text
                    c.data_type = "s"
                    out.append(c)
                else:
                    out.append(int(val))
            ws.append(out)
    wb.save(path)
