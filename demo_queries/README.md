# GraphDB IDE demo queries

These scripts are meant for a live demo from any IDE (VS Code, PyCharm, Cursor, etc.).
They use `requests` and GraphDB's SPARQL HTTP endpoint directly.

## Target repository

By default the scripts query:

- GraphDB base: `http://127.0.0.1:7200`
- repository: `LINDAS_PoC_2`

Adjust defaults in `graphdb_query_utils.py` if needed.

## Install dependency

```bash
pip install requests
```

## Scripts

- `01_classes_mapped_to_ifc.py`
  - asks: *Which local classes map to IFC class `IfcSpace`?*
- `02_class_details_by_ifc.py`
  - asks: *Show richer details for those mapped classes*
- `03_overview_counts.py`
  - asks: *What kinds of RDF resources exist in the graph?*
- `04_properties_for_ifc_pset.py`
  - asks: *Which published properties align to a given IFC property set?*

## Why this matches the AreaMgmt workbook

In the AreaMgmt workbook (`Classes.IFC_URI`), the IFC class URI is carried into RDF as:

- `skos:exactMatch <IFC class URI>`

For example, rows in the workbook using:

- `https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcSpace`

become RDF classes that can be queried through `skos:exactMatch`.
