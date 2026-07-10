# Minimales DD-Publikationsvokabular

Namespace-Vorschlag:

- `dd: <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/>`

Zweck:
Ein schlankes Strukturvokabular für publizierte Data Dictionaries. Es ersetzt **nicht** IFC, QUDT, SKOS, DCAT oder PROV. Es beschreibt nur die dictionary-interne Publikationsstruktur.

## Klassen

- `dd:DataDictionary`
  - ein publiziertes Data Dictionary
- `dd:GroupOfProperties`
  - eine logische Gruppierung / ein Property Set / eine GoP aus der Arbeitsmappe
- `dd:AllowedValue`
  - ein erlaubter Wert / ein Enumerationseintrag, publiziert aus dem Tab `Values`

## Properties

- `dd:hasClass`
  - Dictionary -> Klasse
- `dd:hasProperty`
  - Dictionary -> Property oder Klasse -> Property, abhängig vom Subjekt
- `dd:hasGroupOfProperties`
  - Dictionary -> Group of Properties
- `dd:hasAllowedValue`
  - Property -> erlaubter Wert
- `dd:inGroupOfProperties`
  - Property -> Group of Properties
- `dd:groupContainsProperty`
  - Group of Properties -> Property
- `dd:valueOfProperty`
  - erlaubter Wert -> Property
- `dd:alignedWithIfcPset`
  - Gruppe/Property -> IFC-Property-Set-URI
- `dd:alignedWithIfcPredefinedType`
  - Wert -> IFC-Predefined-Type-URI
- `dd:dictionaryRecord`
  - semantische Ressource -> I14Y-Dataset-/Katalogeintrag-URI

## Alignment-Regeln

- `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch`, `skos:relatedMatch` für semantische Mappings verwenden.
- `qudt:hasUnit` für QUDT-Unit-Links verwenden.
- `dcterms:source` / `prov:wasDerivedFrom` für Provenienz verwenden.
- IFC-URIs als SSOT-Anker verwenden und niemals überschreiben.

## Design-Absicht

Dieses Vokabular ist bewusst minimal gehalten, damit ein schlank publiziertes Data Dictionary einfach abfragbar bleibt und dennoch ausreichend reichhaltig ist, um später gegen IFC-abgeleitete RDF-Graphen validiert werden zu können.
