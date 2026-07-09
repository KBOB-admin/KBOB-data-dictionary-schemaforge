# LINDAS publication readiness

Tomorrow, to publish immediately, only these steps should be needed:

## 1. Provide credentials

Copy:

- `external/lindas.ini.template` -> `external/lindas.ini`

Fill the `INT` section with the provided token/credentials.

## 2. Publish to INT

```bash
python scripts/publish_to_lindas.py \
  --config external/lindas.ini \
  --environment INT \
  --graph https://lindas.admin.ch/fobl/kbob/dd-fm \
  --publish
```

Optional full refresh:

```bash
python scripts/publish_to_lindas.py \
  --config external/lindas.ini \
  --environment INT \
  --graph https://lindas.admin.ch/fobl/kbob/dd-fm \
  --clear-graph \
  --publish
```

## 3. Query channels ready

Prepared now:

- Python / pyLINDAS-adjacent example:
  - `examples/pylindas_query_example.py`
- direct SPARQL examples:
  - `docs/lindas-int-queries.md`
- third access channel:
  - HTTP dereferencing via `curl -H 'Accept: text/turtle' <resource-iri>`

## Notes

- Current graph artifact: `out/combined.ttl`
- Current graph namespace: `https://lindas.admin.ch/fobl/kbob/dd-fm`
- Current publication model includes:
  - classes
  - properties
  - group of properties
  - values / allowed values where workbook evidence exists
  - SKOS cross-dictionary links
  - IFC SSOT links
  - QUDT unit links
