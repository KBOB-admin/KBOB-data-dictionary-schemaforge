# I14Y- und LINDAS-PoC-Mapping

## Zwecktrennung

- **I14Y**: Metadatenkatalog / Registry für Auffindbarkeit, Governance und API-basierte Publikationsdatensätze.
- **LINDAS**: autoritatives Linked-Data-Publikationsziel mit dereferenzierbaren IRIs und RDF.

## Quelle der API-Spezifikation

OpenAPI-Dateien wurden aus `I14Y-ch/apiconsole` extrahiert:

- `external/apiconsole__partner__v1__Release.json`
- `external/apiconsole__public__v1__Release.json`
- `external/apiconsole__partner__v1__configUrl.json`
- `external/apiconsole__public__v1__configUrl.json`

Wichtige identifizierte Partner-Endpunkte:

- `POST /datasets` -> `DcatDatasetInputModelDataWrapper`
- `POST /concepts` -> `ConceptInputBaseDataWrapper`
- `POST /concepts/{conceptId}/codelist-entries/imports/{dataFormat}`
- `POST /catalogs/{catalogId}/records`

ABN-/Integrationsserver gemäss Spezifikation:

- `https://api-a.i14y.admin.ch/api/partner/v1/`

PROD-Server gemäss Spezifikation:

- `https://api.i14y.admin.ch/api/partner/v1/`

## Erforderliche Partner-Payload-Felder

### Dataset (`DcatDatasetInputModel`)

Gemäss Spezifikation erforderlich:

- `accessRights`
- `description`
- `publisher`
- `title`

Aktuelles PoC-Mapping:

- `title` <- primär `Header.DictionaryName (...)`, optional durch `Dictionary_public[Title (...)]` überschrieben
- `description` <- primär `Dictionary_public[Description (...)]`; falls leer, nur generischer Minimaltext aus dem Dictionary-Namen
- `publisher.identifier` <- primär `Header.OrganizationCode`, optional `Dictionary_public[Owner / Publisher]`
- `accessRights.code` <- `Dictionary_public[AccessRights]` oder Fallback `public`
- `issued` / `modified` <- `ReleaseDate` / `ModifiedDate`
- `conformsTo` <- ISO 23386 / optionale DCAT-AP-CH-Links
- `landingPages` <- nur explizite Landing-Page-URL aus `Dictionary_public[MoreInfoUrl]` oder CLI-Override
- `relations` / `documentation` <- optionale URL-Listen aus `Dictionary_public`
- `languages` <- `PrimaryLanguage`, `MetadataLanguages`, sonst aus vorhandenen `Header.DictionaryName (...)`-Sprachen abgeleitet
- `keywords` <- `Dictionary_public[Keywords (...)]`; keine hart codierten Standard-Tags
- `distributions` <- `Dictionary_public[TTL_Download_URL]`, `Dictionary_public[JSON_Download_URL]` sowie optionale Workbook-Download-URL per Workbook-Feld oder CLI-Override

### Concept (`ConceptInputBase` + spezifischer Subtyp)

Gemäss Spezifikation erforderlich:

- `description`
- `name`
- `publisher`
- `responsiblePerson`
- `version`

Aktuelles PoC-Mapping:

- **Classes** -> Export als `String`-Concepts
- **Properties** -> Export als:
  - `CodeList`, wenn Enumerationswerte vorhanden sind
  - `Numeric` für numerische Datentypen / Messgrössen
  - sonst `String`
- `name` <- mehrsprachige Labels aus der Arbeitsmappe
- `description` <- mehrsprachige Definitionen aus der Arbeitsmappe
- `publisher.identifier` <- gleicher Publisher wie beim Dataset
- `responsiblePerson.email` <- `Dictionary_public[ContactEmail]` oder expliziter CLI-Override; kein projekt-spezifischer Fallback mehr
- `version` <- `Version date` der Arbeitsmappe oder Fallback `0.1.0`
- `identifiers` <- Arbeitsmappen-Code + autoritative LINDAS-URI

## Semantische Anker, die niemals verloren gehen dürfen

Diese Anker werden in beiden generierten Artefakten erhalten:

### IFC-SSOT-Verweise

Arbeitsmappen-Spalten:

- Classes: `IFC_URI`, `IfcObject Entity`, `IfcTypeObject Entity`, `PredefinedType`
- Properties: `IFC_URI`, `IfcPropertySet (Pset) / IfcQuantitySet (Qto)`

PoC-Behandlung:

- In **I14Y JSON** werden IFC-URIs in `conformsTo[]` als Ressourcen-Links erhalten.
- In **LINDAS RDF** werden IFC-URIs als `skos:exactMatch`-Links erhalten.
- IFC-Entity- und Predefined-Type-Informationen werden als RDF-Kommentare erhalten.

### QUDT-Unit-SSOT-Verweise

Arbeitsmappen-Spalten:

- Properties: `QUDT URI`, `Unit Name (EN)` und lokale Sprachlabels für Einheiten

PoC-Behandlung:

- In **I14Y JSON** werden QUDT-URIs in `conformsTo[]` erhalten.
- In **LINDAS RDF** werden QUDT-URIs über `qudt:hasUnit` erhalten.

### SKOS-ConceptRelation-Anker

Arbeitsmappen-Tab:

- `ConceptRelation`

PoC-Behandlung:

- Im **I14Y-Bundle** werden Relationen unter `semantic.skosRelations` auf oberster Ebene erhalten.
- In **LINDAS RDF** werden Relationen direkt mit dem deklarierten SKOS-Prädikat ausgegeben (`skos:exactMatch`, `skos:broadMatch` usw.).

## Cross-Link-Strategie

### I14Y -> LINDAS

Jeder Concept-Payload behält die autoritative LINDAS-URI in:

- `identifiers[]`
- `conformsTo[]` als `LINDAS authoritative ... IRI`

### LINDAS -> I14Y

Jede RDF-Ressource enthält Provenienz-Links zum kanonischen versionierten LINDAS-Data-Dictionary:

- `dcterms:source`
- `prov:wasDerivedFrom`

SchemaForge erzeugt keine i14y-URI aus Workbook-Dateinamen. Eine reale, bereits bekannte i14y-Dataset-URI kann optional in `Header.I14yDatasetUri` angegeben werden und wird dann ausschliesslich als `dcat:landingPage` am versionierten Dictionary ausgegeben. Die i14y-Exportpipeline verwaltet ihren eigenen Record-Identifier unabhängig von der LINDAS-RDF-Identität.

## Aktuelle generierte Artefakte

- I14Y-Bundle: `out/i14y_bundle.json`
- LINDAS-RDF-Bundle: `out/combined.ttl`

## Hinweise / verbleibende Lücken

- Der reale I14Y-Publisher ist noch nicht gegen die Live-Partner-API implementiert.
- Die Tabs **Structure** und **Quality information** werden nicht durch `POST /datasets` befüllt.
  - `Structure` hat einen eigenen Endpunkt: `POST /datasets/{datasetId}/structures/imports`
  - Für **Quality information** ist in der vorhandenen Partner-API-Spezifikation kein entsprechender JSON-Import-Endpunkt sichtbar; diese Angaben müssen derzeit separat gepflegt werden.
- Der Code-List-Entry-Import wird noch nicht an den dedizierten I14Y-Endpunkt gepusht; Einträge bleiben im Bundle unter `codeListEntries` erhalten.
- Sobald nach einem POST reale I14Y-Record-URIs verfügbar sind, sollte das Bundle aktualisiert werden, damit RDF-Provenienz auf den erzeugten Record statt auf das Platzhaltermuster verweist.
