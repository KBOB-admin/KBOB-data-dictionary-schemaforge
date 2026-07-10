# KBOB Data Dictionary SchemaForge

Öffentliche Publikationspipeline zur Transformation validierter KBOB-Data-Dictionary-Arbeitsmappen in:

- RDF/Turtle, ausgerichtet auf eine Publikation in LINDAS INT
- ein I14Y-orientiertes JSON-Bundle für Katalog- und Import-Workflows

> **Wichtiger Hinweis:** Das Repository `KBOB-data-dictionary-schemaforge` ist derzeit ein Arbeitsrepository. Aktuell werden **keine Supportleistungen**, **keine individuelle Hilfestellung**, **keine Kontaktadresse** und **kein betreuter Kommunikationskanal** angeboten. Bitte nutzen Sie die bereitgestellten Dateien und Hinweise ausschliesslich in eigener Verantwortung.

## Geltungsbereich

Dieses Repository stellt ein Publikationshilfsmittel für validierte Data Dictionaries bereit.
Es baut auf dem Repository [`KBOB-data-dictionary`](https://github.com/KBOB-admin/KBOB-data-dictionary) auf und verwendet validierte Data-Dictionary-Arbeitsmappen als Eingabe.
Wenn die Validierung systemgenerierte Daten oder sichere Normalisierungen in eine validierte Arbeitsmappe zurückschreibt, können auch diese angereicherten Data Dictionaries als Input für diese Publikationspipeline verwendet werden.

Aktueller Fokus:

- validierte Arbeitsmappen als Eingabe verwenden
- IFC 4.3, QUDT, SKOS und Provenienz-Anker erhalten
- RDF für LINDAS INT exportieren
- ein I14Y-konformes Bundle für nachgelagerte Publikationsarbeiten exportieren

## Erwartete Eingaben

Die aktive Pipeline wird derzeit gegen validierte Arbeitsmappenvarianten ausgeführt, zum Beispiel:

- `templates/Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx`
- `templates/Data Dictionary_BdCH_AreaMgmt_v0.9.6.xlsx`

Die Erzeugung validierter Arbeitsmappen, die strukturellen Prüfungen und die validatorseitigen Rückschreibungen liegen im Repository [`KBOB-data-dictionary`](https://github.com/KBOB-admin/KBOB-data-dictionary).

## Repository-Struktur

- `scripts/` - aktive Transformations- und Publikationsskripte
- `docs/` - Mapping-Notizen und Publikationsdokumentation
- `external/` - Referenzspezifikationen und Templates für Reproduzierbarkeit
- `templates/` - Arbeitsmappenbeispiele und Templates für Pipeline-Arbeiten
- `examples/` - minimale Nutzungsbeispiele
- `demo_queries/` - GraphDB-/LINDAS-Abfragebeispiele

## Reproduzierbarkeitsprinzipien

Dieses öffentliche Repository soll nur Artefakte enthalten, die für die Reproduzierbarkeit relevant sind.
Lokale Ausgaben und Umgebungen sind ausgeschlossen, insbesondere:

- Python-Virtual-Environments
- generierte Exportausgaben unter `out/`
- Caches und `__pycache__`
- editor-spezifische lokale Einstellungen

## Zentrale Skripte

- `scripts/map_to_rdf.py` - Export von Arbeitsmappe nach RDF/Turtle
- `scripts/export_i14y_json.py` - Export von Arbeitsmappe nach I14Y-orientiertem JSON-Bundle
- `scripts/publish_to_lindas.py` - Dry-Run- oder Publikationsschritt für LINDAS INT/PROD

## Nutzung

### RDF-Export

```bash
python scripts/map_to_rdf.py <kbob-workbook.xlsx> <areamgmt-workbook.xlsx> --out out/schemaforge-smoke
```

### I14Y-Bundle-Export

```bash
python scripts/export_i14y_json.py <kbob-workbook.xlsx> <areamgmt-workbook.xlsx> --out out/schemaforge-smoke/i14y_bundle.json
```

### LINDAS-Publikation (standardmässig Dry-Run)

```bash
python scripts/publish_to_lindas.py --ttl out/combined.ttl
```

Eine echte Publikation erfordert explizit `--publish` und lokale Zugangsdaten.
Das Skript unterstützt entweder:

- eine lokale, nicht committete Datei `external/lindas.ini`, oder
- interaktive Eingabe beziehungsweise Umgebungsvariablen für Zugangsdaten und Graph-Einstellungen.

## Hinweise

- Pfade in den aktiven Skripten sind repository-relativ, nicht absolut auf ein Benutzerverzeichnis bezogen.
- Publikation ist standardmässig deaktiviert und soll Dry-Run bleiben, sofern Zugangsdaten und Konfiguration nicht bewusst bereitgestellt werden.
- Dieses Repository ist öffentlich nutzbar, aber nicht automatisch live geschaltet; Publikation bleibt ein expliziter Schritt.
- Zugangsdaten, Graphbestellung, Berechtigungen, Zielgraphen, Freigaben und tatsächliche Publikationshandlungen liegen vollständig in der Verantwortung der nutzenden Organisation.
