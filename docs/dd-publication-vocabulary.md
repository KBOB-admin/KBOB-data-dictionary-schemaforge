# Minimal DD publication vocabulary

Namespace proposal:

- `dd: <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/>`

Purpose:
A thin structural vocabulary for published data dictionaries. It does **not** replace IFC, QUDT, SKOS, DCAT, or PROV. It only expresses dictionary-internal publication structure.

## Classes

- `dd:DataDictionary`
  - a published data dictionary
- `dd:GroupOfProperties`
  - a logical grouping / property set / GoP in the workbook
- `dd:AllowedValue`
  - an allowed value / enumeration member published from the `Values` tab

## Properties

- `dd:hasClass`
  - dictionary -> class
- `dd:hasProperty`
  - dictionary -> property OR class -> property depending on subject
- `dd:hasGroupOfProperties`
  - dictionary -> group of properties
- `dd:hasAllowedValue`
  - property -> allowed value
- `dd:inGroupOfProperties`
  - property -> group of properties
- `dd:groupContainsProperty`
  - group of properties -> property
- `dd:valueOfProperty`
  - allowed value -> property
- `dd:alignedWithIfcPset`
  - group/property -> IFC property set URI
- `dd:alignedWithIfcPredefinedType`
  - value -> IFC predefined type URI
- `dd:dictionaryRecord`
  - semantic resource -> I14Y dataset/catalog record URI

## Alignment rules

- Use `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch`, `skos:relatedMatch` for semantic mappings.
- Use `qudt:hasUnit` for QUDT unit links.
- Use `dcterms:source` / `prov:wasDerivedFrom` for provenance.
- Use IFC URIs as SSOT anchors and never overwrite them.

## Design intent

This vocabulary is intentionally minimal so a lightweight published DD remains easy to query while still being rich enough to validate against IFC-derived RDF graphs later.
