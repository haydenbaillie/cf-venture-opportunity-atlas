"""Build atlas.sqlite from processed and curated tables."""

from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from cf_atlas.paths import external_dir, processed_dir, schema_path, sqlite_path

CURATED_TABLES = {
    "sources": "sources.csv",
    "registry_stats": "registry_stats.csv",
    "unmet_needs": "unmet_needs.csv",
    "therapies": "therapies.csv",
    "programs": "cff_pipeline.csv",
    "strategy_taxonomy": "strategy_taxonomy.csv",
    "scoring_components": "scoring_components.csv",
    "scoring_weights": "scoring_weights.csv",
}

PROCESSED_TABLES = {
    "trials": "trials.csv",
    "trial_interventions": "trial_interventions.csv",
    "trial_collaborators": "trial_collaborators.csv",
}


def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    return header, rows


def _empty_to_none(value: str) -> str | None:
    return value if value != "" else None


def _insert(conn: sqlite3.Connection, table: str, path: Path) -> int:
    header, rows = _read_csv(path)
    placeholders = ", ".join("?" for _ in header)
    columns = ", ".join(header)
    cleaned = [[_empty_to_none(cell) for cell in row] for row in rows]
    conn.executemany(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        cleaned,
    )
    return len(cleaned)


def derive_companies(conn: sqlite3.Connection) -> int:
    conn.execute("DELETE FROM companies")
    conn.execute(
        """
        INSERT INTO companies (company_id, company_name, company_class, source, notes)
        SELECT
            'sponsor:' || lead_sponsor_name,
            lead_sponsor_name,
            lead_sponsor_class,
            'clinicaltrials_gov_api_v2',
            'Derived from lead sponsor on interventional CF trials.'
        FROM trials
        WHERE lead_sponsor_name IS NOT NULL AND trim(lead_sponsor_name) != ''
        GROUP BY lead_sponsor_name, lead_sponsor_class
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO companies (company_id, company_name, company_class, source, notes)
        SELECT
            'program:' || company_name,
            company_name,
            NULL,
            'cff_pipeline_web',
            'Listed on the CFF Drug Development Pipeline page; not a complete company universe.'
        FROM programs
        WHERE company_name IS NOT NULL AND trim(company_name) != ''
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    return int(count)


def build_db(
    *,
    sqlite_file: Path | None = None,
    processed: Path | None = None,
    external: Path | None = None,
) -> dict[str, int | str]:
    processed_root = processed or processed_dir()
    external_root = external or external_dir()
    db_path = sqlite_file or sqlite_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    schema = schema_path().read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript(schema)
        loaded: dict[str, int | str] = {}
        for table, filename in CURATED_TABLES.items():
            path = external_root / filename
            loaded[table] = _insert(conn, table, path)
        for table, filename in PROCESSED_TABLES.items():
            path = processed_root / filename
            if not path.exists():
                raise FileNotFoundError(
                    f"Missing {path}. Run `python -m cf_atlas ingest-trials` first."
                )
            loaded[table] = _insert(conn, table, path)

        loaded["companies"] = derive_companies(conn)
        retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        trial_retrieved = conn.execute(
            "SELECT MIN(retrieved_at), MAX(retrieved_at), COUNT(*) FROM trials"
        ).fetchone()
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("db_built_at", retrieved_at),
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("trials_retrieved_at_min", trial_retrieved[0] or ""),
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("trials_retrieved_at_max", trial_retrieved[1] or ""),
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("trial_count", str(trial_retrieved[2])),
        )
        conn.execute(
            """
            INSERT INTO retrieval_runs (
                run_id, source_id, retrieved_at, query_description,
                record_count, output_path, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"sqlite:{retrieved_at}",
                "clinicaltrials_gov_api_v2",
                retrieved_at,
                "Rebuild of atlas.sqlite from processed snapshots and curated tables",
                trial_retrieved[2],
                str(db_path.as_posix()),
                "Database rebuild. Trial retrieval date is stored on each trials row.",
            ),
        )
        conn.commit()
        loaded["db_built_at"] = retrieved_at
        loaded["sqlite_path"] = str(db_path)
        return loaded
    finally:
        conn.close()
