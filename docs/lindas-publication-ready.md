# LINDAS-Publikationsbereitschaft

Für eine sofortige Publikation sollten nur noch diese Schritte nötig sein:

> **Wichtiger Hinweis:** Dieses Repository stellt nur ein Publikationshilfsmittel bereit. Zugangsdaten, Graphbestellung, Berechtigungen, Zielgraphen, Freigaben und tatsächliche Publikationshandlungen liegen vollständig in der Verantwortung der nutzenden Organisation.

## 1. Zugangsdaten bereitstellen

Entweder:

- `external/lindas.ini.template` nach `external/lindas.ini` kopieren und den Abschnitt `INT` lokal mit Endpoint, Graph, Benutzername/Token und Passwort/Token ausfüllen, oder
- `scripts/publish_to_lindas.py` bei Verwendung von `--publish` interaktiv nach Benutzername/Token, Passwort/Token und Graph fragen lassen.

Die reale Datei `external/lindas.ini` muss lokal bleiben und darf nicht committet werden.

Für eine skalierbare Organisations-Pipeline ist die empfohlene Trennung:

- **Lokaler Testlauf:** `external/lindas.ini` verwenden. Diese Datei ist lokal, nicht versioniert und enthält auch den organisationsspezifischen Graph-Namespace.
- **Wiederholbare Pipeline / GitHub Actions / CI:** Zugangsdaten und Graph-Parameter als Secrets bzw. Umgebungsvariablen bereitstellen (`LINDAS_USERNAME`, `LINDAS_PASSWORD`, `LINDAS_ENDPOINT`, `LINDAS_GRAPH`). Keine Organisation sollte Zugangsdaten in Excel-Dateien, RDF-Artefakte oder Git-Repositories schreiben.
- **Pro Organisation:** Data-Dictionary-Arbeitsmappe ausfüllen, Graph-Namespace und Zugangsdaten beim Bundesarchiv / LINDAS-Betrieb beantragen, validieren, RDF erzeugen, dann mit organisationsspezifischem Graph publizieren.
- **Semantische Verknüpfung:** Die mandatorischen IFC-Anker bleiben im RDF erhalten und dienen als stabiler gemeinsamer Bezugspunkt, um mehrere Data Dictionaries über LINDAS hinweg vergleichbar und mappbar zu machen.

## 2. Nach INT publizieren

```bash
python scripts/publish_to_lindas.py \
  --config external/lindas.ini \
  --environment INT \
  --publish
```

Optionaler vollständiger Refresh:

```bash
python scripts/publish_to_lindas.py \
  --config external/lindas.ini \
  --environment INT \
  --clear-graph \
  --publish
```

## 3. Abfragekanäle sind vorbereitet

Jetzt vorbereitet:

- Python- / pyLINDAS-nahes Beispiel:
  - `examples/pylindas_query_example.py`
- direkte SPARQL-Beispiele:
  - `docs/lindas-int-queries.md`
- dritter Zugriffskanal:
  - HTTP-Dereferenzierung über `curl -H 'Accept: text/turtle' <resource-iri>`

## Hinweise

- Aktuelles Graph-Artefakt: `out/combined.ttl`
- Aktueller Beispiel-Graph-Namespace: `https://lindas.admin.ch/fobl/kbob/dd-fm`
- Das aktuelle Publikationsmodell umfasst:
  - Klassen
  - Properties
  - Groups of Properties
  - Werte / erlaubte Werte, sofern Nachweise in der Arbeitsmappe vorhanden sind
  - dictionary-übergreifende SKOS-Links
  - IFC-SSOT-Links
  - QUDT-Unit-Links
