# I14Y + LINDAS PoC mapping

## Purpose split

- **I14Y**: metadata catalogue / registry for discoverability, governance, and API-based publication records.
- **LINDAS**: authoritative linked-data publication target with dereferenceable IRIs and RDF.

## API spec source

OpenAPI files were extracted from `I14Y-ch/apiconsole`:

- `external/apiconsole__partner__v1__Release.json`
- `external/apiconsole__public__v1__Release.json`
- `external/apiconsole__partner__v1__configUrl.json`
- `external/apiconsole__public__v1__configUrl.json`

Important partner endpoints identified:

- `POST /datasets` → `DcatDatasetInputModelDataWrapper`
- `POST /concepts` → `ConceptInputBaseDataWrapper`
- `POST /concepts/{conceptId}/codelist-entries/imports/{dataFormat}`
- `POST /catalogs/{catalogId}/records`

ABN / integration server from spec:

- `https://api-a.i14y.admin.ch/api/partner/v1/`

PROD server from spec:

- `https://api.i14y.admin.ch/api/partner/v1/`

## Required partner payload fields

### Dataset (`DcatDatasetInputModel`)
Required by spec:

- `accessRights`
- `description`
- `publisher`
- `title`

Current PoC mapping:

- `title` ← inferred workbook title / `Dictionary_public` title fields if present
- `description` ← `Dictionary_public` description fields, fallback generated text
- `publisher.identifier` ← `Dictionary_public[Owner / Publisher]` or inferred org id (`kbob` / `bdch`)
- `accessRights.code` ← `Dictionary_public[AccessRights]` or fallback `public`
- `issued` / `modified` ← `ReleaseDate` / `ModifiedDate`
- `conformsTo` ← ISO 23386 / optional DCAT-AP CH links
- `landingPages` ← fallback I14Y dataset URI plus optional `MoreInfoUrl`
- `relations` / `documentation` ← optional URL lists from `Dictionary_public`

### Concept (`ConceptInputBase` + specific subtype)
Required by spec:

- `description`
- `name`
- `publisher`
- `responsiblePerson`
- `version`

Current PoC mapping:

- **Classes** → exported as `String` concepts
- **Properties** → exported as:
  - `CodeList` when enumeration values are present
  - `Numeric` for numeric / measure datatypes
  - `String` otherwise
- `name` ← multilingual labels from workbook
- `description` ← multilingual definitions from workbook
- `publisher.identifier` ← same publisher as dataset
- `responsiblePerson.email` ← `ContactEmail` or placeholder until real value exists
- `version` ← workbook `Version date` or fallback `0.1.0`
- `identifiers` ← workbook code + authoritative LINDAS URI

## Semantic anchors that must never be lost

These are preserved in both generated artifacts:

### IFC SSOT pointers

Workbook columns:

- Classes: `IFC_URI`, `IfcObject Entity`, `IfcTypeObject Entity`, `PredefinedType`
- Properties: `IFC_URI`, `IfcPropertySet (Pset) / IfcQuantitySet (Qto)`

PoC handling:

- In **I14Y JSON**, IFC URIs are preserved in `conformsTo[]` as resource links.
- In **LINDAS RDF**, IFC URIs are preserved as `skos:exactMatch` links.
- IFC entity / predefined-type information is preserved as RDF comments.

### QUDT unit SSOT pointers

Workbook columns:

- Properties: `QUDT URI`, `Unit Name (EN)` and local-language unit labels

PoC handling:

- In **I14Y JSON**, QUDT URIs are preserved in `conformsTo[]`.
- In **LINDAS RDF**, QUDT URIs are preserved via `qudt:hasUnit`.

### SKOS ConceptRelation anchors

Workbook sheet:

- `ConceptRelation`

PoC handling:

- In **I14Y bundle**, relations are preserved in top-level `semantic.skosRelations`.
- In **LINDAS RDF**, relations are emitted directly using the declared SKOS predicate (`skos:exactMatch`, `skos:broadMatch`, etc.).

## Cross-link strategy

### I14Y → LINDAS

Each concept payload keeps the authoritative LINDAS URI in:

- `identifiers[]`
- `conformsTo[]` as `LINDAS authoritative ... IRI`

### LINDAS → I14Y

Each RDF resource includes provenance links back to the I14Y dataset URI:

- `dcterms:source`
- `prov:wasDerivedFrom`

Dataset URI pattern currently used in PoC:

- `https://i14y.admin.ch/catalog/<slug-of-workbook>`

This is a placeholder until the real I14Y created dataset/record URI is known.

## Current generated artifacts

- I14Y bundle: `out/i14y_bundle.json`
- LINDAS RDF bundle: `out/combined.ttl`

## Notes / remaining gaps

- Real I14Y publisher is not yet implemented against the live Partner API.
- `responsiblePerson.email` currently falls back to `placeholder@example.org` if not present.
- Code list entry import is not yet pushed to the dedicated I14Y endpoint; entries are preserved in the bundle under `codeListEntries`.
- Once real I14Y record URIs are available after POST, the bundle should be updated so RDF provenance references the created record instead of the placeholder pattern.
