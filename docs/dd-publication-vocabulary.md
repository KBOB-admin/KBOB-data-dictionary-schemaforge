# Minimales DD-Publikationsvokabular

Namespace:

- `dd: <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/>`

Zweck:
Ein schlankes Strukturvokabular fuer publizierte Data Dictionaries. Es ersetzt nicht IFC, QUDT, SKOS, DCAT oder PROV. Es beschreibt nur die dictionary-interne Publikationsstruktur.

## Zielmodell

Die Publikation verwendet etablierte Vokabulare zuerst:

- Data-Dictionary-Datensaetze werden als `dcat:Dataset` und `dd:DataDictionary` publiziert.
- Klassen werden als `rdfs:Class` publiziert.
- Properties werden als `rdf:Property` publiziert.
- Enumeration Schemes werden als `skos:ConceptScheme` und `dd:EnumerationScheme` publiziert.
- Einzelne Enumeration Values werden als `skos:Concept`, `dd:EnumerationValue` und vorlaeufig auch als `dd:AllowedValue` publiziert.
- Provenienz wird mit `dcterms:source` und `prov:wasDerivedFrom` erhalten.
- IFC- und QUDT-Links bleiben externe fachliche Anker.

## Klassen

- `dd:DataDictionary`
  - ein publiziertes Data Dictionary
- `dd:GroupOfProperties`
  - eine logische Gruppierung / ein Property Set / eine GoP aus der Arbeitsmappe
- `dd:EnumerationScheme`
  - ein kontrolliertes Enumeration- oder Wertelistenschema aus einer Zeile im Tab `Values`
- `dd:EnumerationValue`
  - ein einzelner Wert innerhalb eines Enumeration Schemes
- `dd:AllowedValue`
  - Rueckwaertskompatibler Typ fuer einzelne erlaubte Werte; derzeit parallel zu `dd:EnumerationValue`

## Properties

- `dd:hasClass`
  - Dictionary -> Klasse
- `dd:hasProperty`
  - Dictionary -> Property
- `dd:hasGroupOfProperties`
  - Dictionary -> Group of Properties
- `dd:hasEnumerationScheme`
  - Dictionary -> Enumeration Scheme
- `dd:usesEnumerationScheme`
  - Property -> Enumeration Scheme
- `dd:enumerationSchemeForProperty`
  - Enumeration Scheme -> Property
- `dd:hasEnumerationValue`
  - Enumeration Scheme -> Enumeration Value
- `dd:hasAllowedValue`
  - Property -> Enumeration Value; rueckwaertskompatibler direkter Zugriffspfad
- `dd:valueOfProperty`
  - Enumeration Value -> Property
- `dd:enumerationPosition`
  - Enumeration Value -> 1-basierte Listenposition im aktuellen Workbook
- `dd:inGroupOfProperties`
  - Property -> Group of Properties
- `dd:groupContainsProperty`
  - Group of Properties -> Property
- `dd:alignedWithIfcPset`
  - Gruppe/Property -> IFC-Property-Set-URI
- `dd:ifcObjectEntity`
  - Klasse -> IFC-Basisklasse
- `dd:ifcPredefinedType`
  - Klasse -> IFC-spezifischer Predefined-Type-Anker
- `dd:dictionaryRecord`
  - semantische Ressource -> I14Y-Dataset-/Katalogeintrag-URI

## SKOS-Regeln fuer Enumerations

Enumeration Schemes werden als `skos:ConceptScheme` modelliert. Einzelwerte sind `skos:Concept` und verweisen auf ihr Schema mit:

```turtle
<.../enumerations/{enumeration-id}/values/{position-token}>
  skos:inScheme <.../enumerations/{enumeration-id}> .
```

`skos:member` wird nicht fuer `skos:ConceptScheme` verwendet, weil `skos:member` formal zu `skos:Collection` passt. `skos:hasTopConcept` wird erst eingefuehrt, wenn Hierarchie oder Top-Concept-Semantik fachlich explizit modelliert wird. Die aktuellen Wertelisten sind flach; `skos:inScheme` reicht fuer die Scheme-Mitgliedschaft.

Multilinguale Labels werden auf Schemes und Values als `skos:prefLabel` publiziert. Aus praktischen Explorer-Gruenden wird derselbe Labelwert zusaetzlich als `rdfs:label` ausgegeben. `skos:notation` wird fuer vorhandene Codes oder den kanonischen Einzelwert verwendet. `rdf:value` wird nur fuer sicher erkennbare numerische oder boolesche Werte gesetzt.

## URI-Strategie fuer Enumeration Values

Das Workbook besitzt derzeit keine expliziten stabilen IDs fuer einzelne Enumeration Values. Fuer das MVP werden Value-URIs deshalb deterministisch aus Enumeration-ID, Listenposition und kanonischem Wert-Token gebildet:

```text
.../enumerations/{Enumeration-ID}/values/{position}-{canonical-token}
```

Beispiel:

```text
https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/area-type-sia-416-code-enum/values/0001-1-2
```

Eigenschaften dieser Strategie:

- deterministisch fuer unveraenderte Workbook-Zeilen;
- duplicate lexical values bleiben unterscheidbar, weil die Listenposition Teil der URI ist;
- mehrsprachige Labels erzeugen keine separaten Ressourcen, sondern Labels auf derselben Ressource;
- Umordnen der Liste aendert Value-URIs;
- Umbenennen des kanonischen englischen Werts aendert ebenfalls den lesbaren URI-Token;
- die aktuelle Strategie ist fuer MVP-Publikation ausreichend, aber nicht langfristig ideal.

Template-Verbesserung fuer das naechste stabile Datenmodell:
Jeder einzelne Enumeration Value sollte im Workbook eine eigene stabile ID oder einen stabilen Code erhalten. Sobald diese Spalte existiert, soll die Value-URI aus dieser ID gebildet werden und nicht mehr aus Position oder Labeltoken.

## Beispiel-RDF

```turtle
@prefix dd: <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum>
  a skos:ConceptScheme, dd:EnumerationScheme ;
  skos:prefLabel "PredefinedType"@en, "Vordefinierter Typ"@de ;
  skos:notation "IFMA_V_31030000" ;
  dd:hasEnumerationValue
    <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum/values/0001-gfa>,
    <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum/values/0002-parking>,
    <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum/values/0003-userdefined> ;
  dct:source <https://i14y.admin.ch/catalog/strukturvorlage-areamgmt-v0-5-0> ;
  prov:wasDerivedFrom <https://i14y.admin.ch/catalog/strukturvorlage-areamgmt-v0-5-0> .

<https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum/values/0002-parking>
  a skos:Concept, dd:EnumerationValue, dd:AllowedValue ;
  skos:inScheme <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum> ;
  skos:prefLabel "PARKING"@en, "PARKING"@de ;
  skos:notation "PARKING" ;
  dd:enumerationPosition 2 ;
  dct:source <https://i14y.admin.ch/catalog/strukturvorlage-areamgmt-v0-5-0> .

<https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/properties/predefinedtype>
  a rdf:Property ;
  dd:usesEnumerationScheme <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum> ;
  dd:hasAllowedValue <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/predefinedtype-enum/values/0002-parking> .
```

## Alignment-Regeln

- `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch`, `skos:relatedMatch` fuer semantische Mappings verwenden.
- `qudt:hasUnit` nur fuer freigegebene QUDT-Unit-URIs verwenden.
- `dcterms:source` / `prov:wasDerivedFrom` fuer Provenienz verwenden.
- IFC-URIs als SSOT-Anker verwenden und niemals ueberschreiben.

## Design-Absicht

Dieses Vokabular ist bewusst minimal gehalten, damit ein schlank publiziertes Data Dictionary einfach abfragbar bleibt und dennoch ausreichend reichhaltig ist, um spaeter gegen IFC-abgeleitete RDF-Graphen validiert werden zu koennen.
