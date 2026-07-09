#!/bin/bash
set -e
WORKBOOK="$1"
OUTDIR="out"
python3 scripts/normalize_concept_relations.py "$WORKBOOK" --org KBOB --dict bdch --lindas-base https://lindas.admin.ch/fobl/kbob/dd-fm --out "$OUTDIR/concept_relations.csv"
python3 scripts/map_to_lindas.py "$WORKBOOK" --org KBOB --dict bdch --lindas-base https://lindas.admin.ch/fobl/kbob/dd-fm --out "$OUTDIR"
echo "Pipeline done. Output in $OUTDIR"
