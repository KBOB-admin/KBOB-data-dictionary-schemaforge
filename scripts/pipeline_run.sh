#!/bin/bash
set -euo pipefail
OUTDIR="${1:-out}"
KBOB_WB="${2:-templates/Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx}"
AREAMGMT_WB="${3:-templates/Data Dictionary_BdCH_AreaMgmt_v0.9.6.xlsx}"
mkdir -p "$OUTDIR"
python3 scripts/map_to_rdf.py "$KBOB_WB" "$AREAMGMT_WB" --out "$OUTDIR"
python3 scripts/export_i14y_json.py "$KBOB_WB" "$AREAMGMT_WB" --out "$OUTDIR/i14y_bundle.json"
echo "Pipeline done. Output in $OUTDIR"
