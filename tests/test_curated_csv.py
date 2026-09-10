from __future__ import annotations

import csv
from pathlib import Path

from cf_atlas.paths import external_dir


def test_curated_csvs_have_rectangular_rows():
    for path in sorted(external_dir().glob("*.csv")):
        rows = list(csv.reader(path.open(encoding="utf-8")))
        header = rows[0]
        for i, row in enumerate(rows[1:], start=2):
            if not any(cell.strip() for cell in row):
                continue
            assert len(row) == len(header), f"{path.name} line {i}: {len(row)} != {len(header)}"
