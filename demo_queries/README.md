# GraphDB-IDE-Demoabfragen

Diese Skripte sind für eine Live-Demo aus einer beliebigen IDE gedacht (VS Code, PyCharm, Cursor usw.).
Sie verwenden `requests` und den SPARQL-HTTP-Endpunkt von GraphDB direkt.

## Ziel-Repository

Standardmässig fragen die Skripte ab:

- GraphDB-Basis: `http://127.0.0.1:7200`
- Repository: `LINDAS_PoC_2`

Die Standardwerte können bei Bedarf in `graphdb_query_utils.py` angepasst werden.

## Dependency installieren

```bash
pip install requests
```

## Skripte

- `01_classes_mapped_to_ifc.py`
  - fragt: *Welche lokalen Klassen mappen auf die IFC-Klasse `IfcSpace`?*
- `02_class_details_by_ifc.py`
  - fragt: *Zeige detailliertere Informationen zu diesen gemappten Klassen*
- `03_overview_counts.py`
  - fragt: *Welche Arten von RDF-Ressourcen existieren im Graph?*
- `04_properties_for_ifc_pset.py`
  - fragt: *Welche publizierten Properties sind einem bestimmten IFC Property Set zugeordnet?*

## Warum dies zur AreaMgmt-Arbeitsmappe passt

In der AreaMgmt-Arbeitsmappe (`Classes.IFC_URI`) wird die IFC-Klassen-URI in RDF übernommen als:

- `skos:exactMatch <IFC class URI>`

Zum Beispiel werden Zeilen in der Arbeitsmappe mit:

- `https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcSpace`

zu RDF-Klassen, die über `skos:exactMatch` abgefragt werden können.
