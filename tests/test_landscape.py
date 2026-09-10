import pytest

from cf_atlas.landscape import build_tables, connect, flag_ncfb
from cf_atlas.paths import sqlite_path


def test_ncfb_flag_catches_bronchiectasis_titles():
    assert flag_ncfb("A Phase II Study of Ensifentrine in Non-Cystic Fibrosis Bronchiectasis")
    assert flag_ncfb("Long-term evaluation in NCFB")
    assert flag_ncfb("Hypertonic saline in non-CF bronchiectasis")


def test_ncfb_flag_does_not_catch_ordinary_cf_titles():
    assert flag_ncfb("Beta-cell Response to Incretin Hormones in Cystic Fibrosis") is None
    assert flag_ncfb("4D-710 in Adult Patients With Cystic Fibrosis") is None
    assert flag_ncfb("Safety of ARCT-032 in people with cystic fibrosis") is None


@pytest.mark.skipif(not sqlite_path().exists(), reason="atlas.sqlite is generated locally")
def test_landscape_claims_are_sourced():
    conn = connect()
    try:
        tables = build_tables(conn)
    finally:
        conn.close()
    claims = tables["landscape_claims"]
    assert claims["source_id"].fillna("").ne("").all()
    assert set(claims["layer"]) <= {"fact", "analysis", "interpretation", "hypothesis"}
    assert len(tables["solved_unsolved"]) == 8
    assert set(tables["need_snapshots"]["need_id"]) == {
        "N1",
        "N2",
        "N3",
        "N4",
        "N5",
        "N6",
        "N7",
        "N8",
    }



def test_ncfb_flag_catches_bronchiectasis_titles():
    assert flag_ncfb("A Phase II Study of Ensifentrine in Non-Cystic Fibrosis Bronchiectasis")
    assert flag_ncfb("Long-term evaluation in NCFB")
    assert flag_ncfb("Hypertonic saline in non-CF bronchiectasis")


def test_ncfb_flag_does_not_catch_ordinary_cf_titles():
    assert flag_ncfb("Beta-cell Response to Incretin Hormones in Cystic Fibrosis") is None
    assert flag_ncfb("4D-710 in Adult Patients With Cystic Fibrosis") is None
    assert flag_ncfb("Safety of ARCT-032 in people with cystic fibrosis") is None
