"""Command-line interface for ingest and database rebuild."""

from __future__ import annotations

import argparse
import json
import sys

from cf_atlas.classify import run_classify
from cf_atlas.db import build_db
from cf_atlas.export_app import run_export_app
from cf_atlas.ingest import ingest_trials
from cf_atlas.landscape import run_landscape
from cf_atlas.score import run_score
from cf_atlas.theses import run_theses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cf-atlas",
        description="CF Venture Opportunity Atlas data tools",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser(
        "ingest-trials",
        help="Fetch interventional CF studies from ClinicalTrials.gov API v2",
    )
    ingest.add_argument("--page-size", type=int, default=100)

    sub.add_parser("build-db", help="Rebuild atlas.sqlite from processed and curated tables")

    rebuild = sub.add_parser(
        "rebuild",
        help="Ingest ClinicalTrials.gov then rebuild atlas.sqlite",
    )
    rebuild.add_argument("--page-size", type=int, default=100)

    sub.add_parser(
        "landscape",
        help="Write Phase 3 landscape tables and figures from atlas.sqlite",
    )
    sub.add_parser(
        "classify",
        help="Write Phase 4 classifications and a reviewed-only competitive map",
    )
    sub.add_parser(
        "score",
        help="Write Phase 5 opportunity scores from curated 1-5 rubrics",
    )
    sub.add_parser(
        "theses",
        help="Write challenge memos (docs/theses) from curated thesis JSON",
    )
    sub.add_parser(
        "export-app",
        help="Write dated JSON snapshot for the Next.js app",
    )

    args = parser.parse_args(argv)

    if args.command == "ingest-trials":
        result = ingest_trials(page_size=args.page_size)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "build-db":
        result = build_db()
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "rebuild":
        ingest_result = ingest_trials(page_size=args.page_size)
        db_result = build_db()
        print(json.dumps({"ingest": ingest_result, "database": db_result}, indent=2))
        return 0
    if args.command == "landscape":
        result = run_landscape()
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "classify":
        result = run_classify()
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "score":
        result = run_score()
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "theses":
        result = run_theses()
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "export-app":
        result = run_export_app()
        print(json.dumps(result, indent=2))
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
