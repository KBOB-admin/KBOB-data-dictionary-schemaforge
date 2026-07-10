# LINDAS-Publikationsbereitschaft

Für eine sofortige Publikation sollten nur noch diese Schritte nötig sein:

## 1. Zugangsdaten bereitstellen

Entweder:

- `external/lindas.ini.template` nach `external/lindas.ini` kopieren und den Abschnitt `INT` lokal ausfüllen, oder
- `scripts/publish_to_lindas.py` bei Verwendung von `--publish` interaktiv nach Benutzername/Token, Passwort/Token und Graph fragen lassen.

Die reale Datei `external/lindas.ini` muss lokal bleiben und darf nicht committet werden.

## 2. Nach INT publizieren

```bash
python scripts/publish_to_lindas.py \
  --config external/lindas.ini \
  --environment INT \
  --graph https://lindas.admin.ch/fobl/kbob/dd-fm \
  --publish
```

Optionaler vollständiger Refresh:

```bash
python scripts/publish_to_lindas.py \
  --config external/lindas.ini \
  --environment INT \
  --graph https://lindas.admin.ch/fobl/kbob/dd-fm \
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
- Aktueller Graph-Namespace: `https://lindas.admin.ch/fobl/kbob/dd-fm`
- Das aktuelle Publikationsmodell umfasst:
  - Klassen
  - Properties
  - Groups of Properties
  - Werte / erlaubte Werte, sofern Nachweise in der Arbeitsmappe vorhanden sind
  - dictionary-übergreifende SKOS-Links
  - IFC-SSOT-Links
  - QUDT-Unit-Links
