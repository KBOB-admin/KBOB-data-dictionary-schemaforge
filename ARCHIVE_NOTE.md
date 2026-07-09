ARCHIVE_NOTE.md

This folder archives enriched/INTOP pipeline artifacts that are NOT part of the PoC
LINDAS-mint pipeline currently in active development.

What was archived (moved to archive/):
- schemaforge/ (INTOP-enriched pipeline; rdf_writer.py, readers, ids, validate_strukturvorlage.py)
- HE_SEM_shemaforge/ (HE-SEM workbook sources and generated DD workbooks)

Why archived:
- The PoC that produced out/combined.ttl relies on the lightweight LINDAS-mint
  scripts under scripts/ (map_to_rdf.py, map_to_lindas.py, normalize_concept_relations.py).
- The archived code contains INTOP predicates, IDS generation and bSDD publishing
  helpers that are out of scope for the immediate PoC and publishing goals.

If you need to restore archived code:
- The archived content lives under /home/Dave/.openclaw/workspace-datadict/P_workspace_codat3_schemaforge/archive/
  (schemaforge_old/, HE_SEM_shemaforge_old/).

Git guidance:
- The archive/ folder has been added to .gitignore to avoid accidental commits. If you prefer a different policy,
  modify .gitignore accordingly.

Next steps:
- Focus development on the simple scripts/ pipeline for LINDAS & i14y publishing.
- If/when richer INTOP integration is required, we can selectively reintroduce files from the archive.

Created by: datadict
