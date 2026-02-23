# CV Classification Engine (Database-Driven)

This repository contains a CV classification engine designed for your future Gmail → Vincere pipeline, focused only on classification for now.

## What it does

1. Parses CV text (normalization + phrase matching).
2. Classifies candidates into:
   - **Classification** (top-level)
   - **Sub-family** (required gate)
   - **Specialism(s)** (multi-select)
3. Blocks or flags CVs that fail minimum evidence thresholds.
4. Runs entirely from a database masterlist.
5. Requires zero code changes when keywords are edited in the DB.

## Design

- **Versioned rulesets** in `rulesets`.
- **Node hierarchy** in `rule_nodes`:
  - `classification`
  - `sub_family`
  - `specialism`
- **Keyword lists + weights per node** in `rule_keywords`.
- **Scoring model** (weighted evidence) instead of binary contains.

## Decision states

- `accepted`: classification + sub-family pass, and at least one specialism passes.
- `flagged`: classification + sub-family pass, but no specialism passes.
- `blocked`: classification fails, or required sub-family gate fails.

## Files

- `src/cv_classifier/engine.py` – scoring and decision logic.
- `src/cv_classifier/repository.py` – loads active versioned ruleset from SQLite.
- `src/cv_classifier/types.py` – typed result and rule dataclasses.
- `db/schema.sql` – database schema.
- `db/seed_v1.sql` – starter masterlist/ruleset.
- `scripts_init_db.py` – initializes local SQLite DB (`cv_rules.db`).
- `demo_classify.py` – simple execution example.

## Quickstart

```bash
python scripts_init_db.py
PYTHONPATH=src python demo_classify.py
PYTHONPATH=src python -m unittest discover -s tests
```

## Updating Keywords with No Code Changes

Edit only `rule_keywords` rows for the active ruleset version. The engine loads rules dynamically at runtime.

Example:

```sql
INSERT INTO rule_keywords (ruleset_id, node_id, keyword, weight)
VALUES (1, 301, 'typescript', 1.0);
```

No code deployment needed.

## Versioning Rules

1. Insert a new row in `rulesets` with a new `version`.
2. Add corresponding `rule_nodes` and `rule_keywords` rows.
3. Set `is_active = 1` on the new version and `0` on the old one.

The engine always loads the latest active ruleset.
