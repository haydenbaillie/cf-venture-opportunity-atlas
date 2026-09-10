from pathlib import Path

from cf_atlas.paths import external_dir, repo_root, schema_path


def test_repo_layout_exists():
    root = repo_root()
    assert (root / "pyproject.toml").exists()
    assert (root / "data" / "external" / "unmet_needs.csv").exists()
    assert schema_path().exists()
    assert external_dir() == root / "data" / "external"
    need_ids = Path(external_dir() / "unmet_needs.csv").read_text(encoding="utf-8")
    for need_id in ("N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"):
        assert need_id in need_ids
