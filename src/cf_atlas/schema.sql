PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    organization TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    publication_date TEXT,
    retrieval_date TEXT NOT NULL,
    source_type TEXT NOT NULL,
    access_method TEXT NOT NULL,
    description TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS retrieval_runs (
    run_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    query_description TEXT,
    record_count INTEGER,
    output_path TEXT,
    notes TEXT,
    FOREIGN KEY (source_id) REFERENCES sources (source_id)
);

CREATE TABLE IF NOT EXISTS registry_stats (
    stat_id TEXT PRIMARY KEY,
    metric_key TEXT NOT NULL,
    metric_label TEXT NOT NULL,
    year INTEGER,
    stratum TEXT NOT NULL,
    value_numeric REAL,
    value_text TEXT,
    unit TEXT,
    denominator_notes TEXT,
    population_notes TEXT,
    source_id TEXT NOT NULL,
    report_section TEXT,
    extraction_method TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources (source_id)
);

CREATE TABLE IF NOT EXISTS unmet_needs (
    need_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    subcategory TEXT,
    patient_population TEXT,
    prevalence_or_population TEXT,
    clinical_burden TEXT,
    economic_burden TEXT,
    treatment_gap TEXT,
    pipeline_density TEXT,
    evidence_strength TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS therapies (
    therapy_id TEXT PRIMARY KEY,
    therapy_name TEXT NOT NULL,
    generic_name TEXT,
    company TEXT,
    mechanism TEXT,
    target TEXT,
    modality TEXT,
    indication TEXT,
    development_stage TEXT,
    approval_status TEXT,
    approval_date TEXT,
    genotype_scope TEXT,
    age_scope TEXT,
    application_number TEXT,
    source_id TEXT,
    notes TEXT,
    FOREIGN KEY (source_id) REFERENCES sources (source_id)
);

CREATE TABLE IF NOT EXISTS programs (
    program_id TEXT PRIMARY KEY,
    asset_name TEXT NOT NULL,
    company_name TEXT,
    therapeutic_strategy TEXT,
    mechanism TEXT,
    modality TEXT,
    development_stage TEXT,
    genotype_scope TEXT,
    population_description TEXT,
    cff_listed_status TEXT,
    review_status TEXT NOT NULL,
    source_id TEXT,
    notes TEXT,
    FOREIGN KEY (source_id) REFERENCES sources (source_id)
);

CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    company_class TEXT,
    source TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS trials (
    nct_id TEXT PRIMARY KEY,
    brief_title TEXT,
    official_title TEXT,
    acronym TEXT,
    lead_sponsor_name TEXT,
    lead_sponsor_class TEXT,
    phase TEXT,
    overall_status TEXT,
    study_type TEXT,
    enrollment_count INTEGER,
    enrollment_type TEXT,
    start_date TEXT,
    primary_completion_date TEXT,
    completion_date TEXT,
    why_stopped TEXT,
    sex TEXT,
    minimum_age TEXT,
    maximum_age TEXT,
    std_ages TEXT,
    healthy_volunteers INTEGER,
    eligibility_criteria TEXT,
    brief_summary TEXT,
    conditions TEXT,
    has_results INTEGER,
    is_fda_regulated_drug INTEGER,
    primary_outcomes TEXT,
    retrieved_at TEXT,
    source_id TEXT,
    FOREIGN KEY (source_id) REFERENCES sources (source_id)
);

CREATE TABLE IF NOT EXISTS trial_interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nct_id TEXT NOT NULL,
    intervention_type TEXT,
    intervention_name TEXT,
    description TEXT,
    FOREIGN KEY (nct_id) REFERENCES trials (nct_id)
);

CREATE TABLE IF NOT EXISTS trial_collaborators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nct_id TEXT NOT NULL,
    name TEXT,
    class TEXT,
    FOREIGN KEY (nct_id) REFERENCES trials (nct_id)
);

CREATE TABLE IF NOT EXISTS strategy_taxonomy (
    strategy_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    parent_id TEXT,
    description TEXT,
    cff_pipeline_group TEXT
);

CREATE TABLE IF NOT EXISTS scoring_components (
    component_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    default_weight REAL NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS scoring_weights (
    preset_id TEXT NOT NULL,
    component_id TEXT NOT NULL,
    weight REAL NOT NULL,
    PRIMARY KEY (preset_id, component_id),
    FOREIGN KEY (component_id) REFERENCES scoring_components (component_id)
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trials_status ON trials (overall_status);
CREATE INDEX IF NOT EXISTS idx_trials_phase ON trials (phase);
CREATE INDEX IF NOT EXISTS idx_trials_sponsor_class ON trials (lead_sponsor_class);
CREATE INDEX IF NOT EXISTS idx_registry_metric ON registry_stats (metric_key, year, stratum);
CREATE INDEX IF NOT EXISTS idx_programs_strategy ON programs (therapeutic_strategy);
