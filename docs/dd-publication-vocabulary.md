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
- `dd:Document`
  - ein Dokumenteintrag aus dem Tab `Documents`
- `dd:DataTemplate`
  - eine publizierte Data-Template-Zeile aus dem Tab `Data_Template`
- `dd:PropertyRequirement`
  - eine kontextuelle Property-Anforderung innerhalb eines Data Templates; n-ary Ressource zwischen Data Template, Class und Property

## Properties

- `dd:hasClass`
  - Dictionary -> Klasse
- `dd:hasProperty`
  - Dictionary -> Property
- `dd:hasGroupOfProperties`
  - Dictionary -> Group of Properties
- `dd:hasEnumerationScheme`
  - Dictionary -> Enumeration Scheme
- `dd:hasDocument`
  - Dictionary -> Document
- `dd:hasDataTemplate`
  - Dictionary oder Class -> Data Template
- `dd:appliesToClass`
  - Data Template oder Property Requirement -> Class
- `dd:includesGroupOfProperties`
  - Data Template -> Group of Properties
- `dd:referencesDocument`
  - Data Template, Property Requirement oder Class -> Document
- `dd:hasPropertyRequirement`
  - Data Template -> Property Requirement
- `dd:requirementOfDataTemplate`
  - Property Requirement -> Data Template
- `dd:requiresProperty`
  - Property Requirement -> Property
- `dd:requiredByTemplate`
  - Property -> Property Requirement
- `dd:usesEnumerationScheme`
  - Property oder Property Requirement -> Enumeration Scheme
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
- `dd:allowedValue`
  - Property Requirement -> Enumeration Value; kontextuelle erlaubte Teilmenge
- `dd:usesCompleteValueScheme`
  - Property Requirement -> Boolean; `true` wenn die Property ein Enumeration Scheme besitzt und die Matrixzelle `x` keine Teilmenge einschraenkt
- `dd:inclusionMarker`
  - Property Requirement -> urspruenglicher Matrixzellwert (`x` oder Listenliteral)
- `dd:requirementLevel`
  - Property Requirement -> derzeit `included`; nicht als mandatory/minCount interpretieren
- `dd:contextualDatatype`
  - Property Requirement -> DataType aus der allgemeinen Property-Definition
- `dd:contextualUnit`
  - Property Requirement -> QUDT-URI oder Einheitsliteral aus der allgemeinen Property-Definition
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

## Data Templates und Property Requirements

Die `Data_Template`-Matrix wird als deskriptiver RDF-Layer publiziert. Eine Matrixzeile wird zu einer `dd:DataTemplate`-Ressource. Jede nicht-leere Property-Zelle in dieser Zeile wird zu einer eigenen `dd:PropertyRequirement`-Ressource.

Das ist bewusst ein n-ary Modell:

```text
DataTemplate
  dd:appliesToClass Class ;
  dd:includesGroupOfProperties Group ;
  dd:referencesDocument Document ;
  dd:hasPropertyRequirement PropertyRequirement .

PropertyRequirement
  dd:requiresProperty Property ;
  dd:usesEnumerationScheme EnumerationScheme ;
  dd:allowedValue EnumerationValue .
```

Die Anforderung wird nicht als direkte Class-Property-Kante modelliert, weil Matrixzellen kontextuelle Semantik enthalten: Einbindung, Wertlisten-Teilmenge, Datentyp-/Einheitskontext, Governance und spaeter IDS-relevante Informationen.

### Matrixzellen

- Leere Zelle: keine `dd:PropertyRequirement`.
- `x`: Property ist im Data Template enthalten. Wenn die allgemeine Property ein Enumeration Scheme besitzt, wird `dd:usesEnumerationScheme` auf der Requirement-Ressource gesetzt und `dd:usesCompleteValueScheme true` publiziert.
- JSON-Liste, z. B. `["A", "B"]`: Property ist enthalten und auf eine Teilmenge der bestehenden Enumeration Values eingeschraenkt. Die Requirement-Ressource erhaelt `dd:usesCompleteValueScheme false` und je Wert ein `dd:allowedValue`.

Die allgemeine Property behaelt immer ihre vollstaendige Enumeration-Scheme-Verknuepfung. Requirement-Level-Values sind nur der kontextuelle Ausschnitt.

### Data-Template-URI-Strategie

Das Workbook enthaelt derzeit keine expliziten Data-Template-IDs. Fuer das MVP wird eine deterministische URI aus Matrixzeile, Class-ID und GoP-ID gebildet:

```text
.../data-templates/{row}-{class-id}-{gop-id-or-no-group}
```

Beispiel:

```text
https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/data-templates/0009-room-ifma-areamgmt
```

Diese Strategie ist stabil, solange die Matrixzeilen nicht umsortiert werden. Langfristig sollte das Workbook eine explizite Data-Template-ID oder Assignment-ID erhalten.

Property-Requirement-URIs liegen unter:

```text
.../property-requirements/{data-template-id}/{property-id}
```

### Groups of Properties

`GroupOfProperties` bleibt eine eigenstaendige Ressource. Die Matrixspalte fuer GoP wird als `dd:includesGroupOfProperties` am Data Template und als `dd:inGroupOfProperties` an den Property Requirements publiziert.

Es wird nicht inferiert, dass die Auswahl einer Gruppe automatisch alle Properties der Gruppe einschliesst. Requirements entstehen nur aus explizit nicht-leeren Property-Zellen. Dadurch koennen Teilmengen einer Gruppe ohne doppelte Requirements beschrieben werden.

### Documents

Dokumente aus `Documents` werden als `dd:Document` und `schema:CreativeWork` publiziert. `schema:CreativeWork` wurde gewaehlt, weil die Workbook-Eintraege allgemeine normative oder referenzierende Werke beschreiben koennen und nicht zwingend Web-Dokumente mit Dateizugriff sind. Dokumente erhalten Labels, Identifier, Publisher, Revision, Status, Version date, Provenienz und Dataset-Quelle, soweit vorhanden.

Data Templates verweisen mit `dd:referencesDocument` auf ausgewaehlte Dokumente. Wenn das Workbook keine Dokumentrolle unterscheidet, wird keine Rolle erfunden.

### Cardinality und IDS-Gap

`x` bedeutet im aktuellen RDF nur `included`, nicht mandatory. Es wird kein `minCount = 1` abgeleitet. Das Workbook liefert aktuell keine verlustfreie Semantik fuer:

- required versus optional;
- min/max cardinality;
- exactly-one;
- repeatability;
- Dokumentrolle einer Anforderung;
- explizite Data-Template-ID;
- explizite Property-Requirement-ID;
- explizite Value-ID fuer Enumeration Values.

Diese Felder sind fuer einen spaeteren IDS-Export relevant und sollten im Template ergaenzt werden, bevor SHACL/IDS als normative Ausgabe stabilisiert wird.

### Override-Aufloesung

Override-Werte werden nur auf bereits publizierte Enumeration Values gemappt. Es werden keine neuen Values aus Matrixzellen erzeugt.

Die Aufloesung sucht ueber die kanonischen Werte und vorhandene mehrsprachige Labels derselben Enumeration Values. Dadurch erzeugen deutsche oder andere Sprachlabels keine getrennten Ressourcen.

Wenn ein Override-Wert auf mehrere bestehende Enumeration Values passt, weil die Quelle doppelte lexikalische Werte enthaelt und noch keine Value-IDs besitzt, werden alle passenden bestehenden Values verknuepft und eine Mapper-Warnung geschrieben. Sobald value-level IDs existieren, sollte die Matrix auf diese IDs referenzieren.
