# KBOB Data Dictionary SchemaForge

Public-facing MVP pipeline for transforming validated KBOB data dictionary workbooks into:
- RDF/Turtle aligned for LINDAS INT publication
- an I14Y-oriented JSON bundle for catalog/import workflows

## Scope

This repository is intentionally limited to the SchemaForge MVP publication path.
It is not the validator repository and it is not the full historical authoring workspace.

Current MVP focus:
- consume validated workbook inputs
- preserve IFC 4.3, QUDT, SKOS, and provenance anchors
- export RDF for LINDAS INT
- export an I14Y-conform bundle for downstream publication work

## Expected inputs

The active pipeline is currently exercised against validated workbook variants such as:
- `Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx`
- `Data Dictionary_BdCH_AreaMgmt_v0.9.6.xlsx`

Validated workbook generation and structural checks live in the separate validator repository.

## Repository structure

- `scripts/` — active transformation and publication scripts
- `docs/` — mapping notes and publication documentation
- `external/` — reference specifications/templates required for reproducibility
- `templates/` — workbook examples/templates used for pipeline work
- `examples/` — minimal usage examples
- `demo_queries/` — GraphDB/LINDAS query examples

## Reproducibility principles

This public repository should contain only artefacts relevant for reproducibility.
Local-only outputs and environments are excluded, including:
- Python virtual environments
- generated export output under `out/`
- caches and `__pycache__`
- editor-specific local settings

## Core scripts

- `scripts/map_to_rdf.py` — workbook to RDF/Turtle export
- `scripts/export_i14y_json.py` — workbook to I14Y-oriented JSON bundle export
- `scripts/publish_to_lindas.py` — dry-run or publish step for LINDAS INT/PROD

## Usage

### RDF export

```bash
python scripts/map_to_rdf.py <kbob-workbook.xlsx> <areamgmt-workbook.xlsx> --out out/schemaforge-smoke
```

### I14Y bundle export

```bash
python scripts/export_i14y_json.py <kbob-workbook.xlsx> <areamgmt-workbook.xlsx> --out out/schemaforge-smoke/i14y_bundle.json
```

### LINDAS publish (dry-run by default)

```bash
python scripts/publish_to_lindas.py --ttl out/combined.ttl
```

Real publication requires a valid `external/lindas.ini` and explicit `--publish`.

## Notes

- Paths inside active scripts are repo-relative, not user-home absolute.
- Publication is disabled by default and should remain dry-run unless credentials/config are intentionally provided.
- This repository is public-facing but not automatically live; publication remains an explicit step.
