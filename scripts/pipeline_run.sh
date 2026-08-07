#!/bin/bash
set -euo pipefail
OUTDIR="${1:-out}"
shift || true
WORKBOOKS=("$@")
if [ "${#WORKBOOKS[@]}" -eq 0 ]; then
  WORKBOOKS=(
    "templates/Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx"
    "templates/Strukturvorlage_AreaMgmt_v0.5.0.xlsx"
  )
fi
mkdir -p "$OUTDIR"
python3 scripts/map_to_rdf.py "${WORKBOOKS[@]}" --out "$OUTDIR"
python3 scripts/export_i14y_json.py "${WORKBOOKS[@]}" --out "$OUTDIR/i14y_bundle.json"
echo "Pipeline done. Output in $OUTDIR"
