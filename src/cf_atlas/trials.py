"""Parse ClinicalTrials.gov Data API v2 study records into tidy rows."""

from __future__ import annotations

from typing import Any


def nested_get(data: Any, *keys: str, default: Any = None) -> Any:
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _join(values: list[Any] | None, sep: str = " | ") -> str | None:
    if not values:
        return None
    parts = [str(v).strip() for v in values if v is not None and str(v).strip()]
    return sep.join(parts) if parts else None


def _date(struct: Any) -> str | None:
    if isinstance(struct, dict):
        return struct.get("date")
    return None


def _bool_int(value: Any) -> int | None:
    if value is True:
        return 1
    if value is False:
        return 0
    return None


def flatten_trial(study: dict[str, Any], retrieved_at: str, source_id: str) -> dict[str, Any]:
    protocol = study.get("protocolSection") or {}
    ident = protocol.get("identificationModule") or {}
    status = protocol.get("statusModule") or {}
    sponsor = protocol.get("sponsorCollaboratorsModule") or {}
    design = protocol.get("designModule") or {}
    eligibility = protocol.get("eligibilityModule") or {}
    outcomes = protocol.get("outcomesModule") or {}
    conditions = protocol.get("conditionsModule") or {}
    description = protocol.get("descriptionModule") or {}
    oversight = protocol.get("oversightModule") or {}
    lead = sponsor.get("leadSponsor") or {}
    enrollment = design.get("enrollmentInfo") or {}
    primary_outcomes = outcomes.get("primaryOutcomes") or []

    nct_id = ident.get("nctId")
    if not nct_id:
        raise ValueError("Study record is missing NCT ID")

    return {
        "nct_id": nct_id,
        "brief_title": ident.get("briefTitle"),
        "official_title": ident.get("officialTitle"),
        "acronym": ident.get("acronym"),
        "lead_sponsor_name": lead.get("name"),
        "lead_sponsor_class": lead.get("class"),
        "phase": _join(design.get("phases"), sep=";"),
        "overall_status": status.get("overallStatus"),
        "study_type": design.get("studyType"),
        "enrollment_count": enrollment.get("count"),
        "enrollment_type": enrollment.get("type"),
        "start_date": _date(status.get("startDateStruct")),
        "primary_completion_date": _date(status.get("primaryCompletionDateStruct")),
        "completion_date": _date(status.get("completionDateStruct")),
        "why_stopped": status.get("whyStopped"),
        "sex": eligibility.get("sex"),
        "minimum_age": eligibility.get("minimumAge"),
        "maximum_age": eligibility.get("maximumAge"),
        "std_ages": _join(eligibility.get("stdAges"), sep=";"),
        "healthy_volunteers": _bool_int(eligibility.get("healthyVolunteers")),
        "eligibility_criteria": eligibility.get("eligibilityCriteria"),
        "brief_summary": description.get("briefSummary"),
        "conditions": _join(conditions.get("conditions")),
        "has_results": _bool_int(study.get("hasResults")),
        "is_fda_regulated_drug": _bool_int(oversight.get("isFdaRegulatedDrug")),
        "primary_outcomes": _join(
            [item.get("measure") for item in primary_outcomes if isinstance(item, dict)]
        ),
        "retrieved_at": retrieved_at,
        "source_id": source_id,
    }


def flatten_interventions(study: dict[str, Any]) -> list[dict[str, Any]]:
    nct_id = nested_get(study, "protocolSection", "identificationModule", "nctId")
    interventions = (
        nested_get(study, "protocolSection", "armsInterventionsModule", "interventions") or []
    )
    rows: list[dict[str, Any]] = []
    for item in interventions:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "nct_id": nct_id,
                "intervention_type": item.get("type"),
                "intervention_name": item.get("name"),
                "description": item.get("description"),
            }
        )
    return rows


def flatten_collaborators(study: dict[str, Any]) -> list[dict[str, Any]]:
    nct_id = nested_get(study, "protocolSection", "identificationModule", "nctId")
    collaborators = (
        nested_get(study, "protocolSection", "sponsorCollaboratorsModule", "collaborators") or []
    )
    rows: list[dict[str, Any]] = []
    for item in collaborators:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "nct_id": nct_id,
                "name": item.get("name"),
                "class": item.get("class"),
            }
        )
    return rows
