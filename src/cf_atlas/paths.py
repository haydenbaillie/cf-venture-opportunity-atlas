"""Path helpers for the CF Venture Opportunity Atlas repo."""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not locate repository root (no pyproject.toml).")


def data_dir() -> Path:
    return repo_root() / "data"


def raw_dir() -> Path:
    return data_dir() / "raw"


def processed_dir() -> Path:
    return data_dir() / "processed"


def external_dir() -> Path:
    return data_dir() / "external"


def sqlite_path() -> Path:
    return processed_dir() / "atlas.sqlite"


def schema_path() -> Path:
    return PACKAGE_DIR / "schema.sql"
