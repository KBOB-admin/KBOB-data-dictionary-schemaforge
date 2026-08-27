# Minimales DD-Publikationsvokabular

Normative Quelle und öffentliche Versionshistorie:

- [`KBOB-data-dictionary-schema`](https://github.com/KBOB-admin/KBOB-data-dictionary-schema)
- [aktuelles Turtle-Artefakt](https://raw.githubusercontent.com/KBOB-admin/KBOB-data-dictionary-schema/main/ontology/natdd-core.ttl)

Dieses Dokument beschreibt, wie SchemaForge das Vokabular verwendet. Es ist keine zweite normative Begriffsdefinition. Bei Abweichungen ist das Schema-Repository maßgebend.

Namespace:

- `dd: <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/>`

Zweck:
Ein schlankes Strukturvokabular fuer publizierte Data Dictionaries. Es ersetzt nicht IFC, QUDT, SKOS, DCAT oder PROV. Es beschreibt nur die dictionary-interne Publikationsstruktur.

## Zielmodell

Die Publikation verwendet etablierte Vokabulare zuerst:

- Data-Dictionary-Datensaetze werden als `dcat:Dataset` und `dd:DataDictionary` publiziert. Das nutzerseitige Dictionary-Label stammt aus `Header.DictionaryName (...)`; die konkrete Excel-Datei wird als `prov:Entity` mit `dcterms:identifier` modelliert und ueber `prov:wasDerivedFrom` sowie `dcterms:source` verknuepft.
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
  - ein ueber `DataTemplate-ID` identifiziertes Template aus dem Tab `Data_Template`; mehrere Zeilen duerfen zu demselben Template beitragen
- `dd:DocumentType`
  - zusaetzlicher Typ fuer terminale Klassen eines als `Document type taxonomy` gekennzeichneten Klassenbestands
- `dd:TaxonomyNode`
  - zusaetzlicher Typ fuer nicht-terminale Navigationsknoten eines als `Document type taxonomy` gekennzeichneten Klassenbestands

Bei einer Dokumenttyp-Taxonomie bleibt jede Ressource zugleich `rdfs:Class`. Die
naechste vorhandene uebergeordnete Klasse wird standardkonform mit
`rdfs:subClassOf` publiziert. Der `Class-Code` wird als `skos:notation`
ausgegeben. Dadurch koennen terminale Dokumenttypen getrennt gezaehlt und die
Taxonomieknoten weiterhin hierarchisch durchsucht werden.
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
  - Dictionary -> Data Template
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
  - Property Requirement -> Group of Properties im jeweiligen Data-Template-Kontext
- `dd:alignedWithIfcPset`
  - Gruppe/Property -> IFC-Property-Set-URI
- `dd:ifcObjectEntity`
  - Klasse -> IFC-Basisklasse
- `dd:ifcPredefinedType`
  - Klasse -> IFC-spezifischer Predefined-Type-Anker
- `dd:dictionaryRecord`
  - semantische Ressource -> I14Y-Dataset-/Katalogeintrag-URI
- `dd:datatype`
  - Property -> `Properties.DataType (Base Type)` als publizierter Basisdatentyp
- `dd:ifcDatatype`
  - Property -> `Properties.DataType (IFC)` als publizierter IFC-Datentyp
- `dd:status`
  - Document, Property oder Data Template -> Lifecycle-/Governance-Status aus dem Workbook

## SKOS-Regeln fuer Enumerations

Enumeration Schemes werden als `skos:ConceptScheme` modelliert. Einzelwerte sind `skos:Concept` und verweisen auf ihr Schema mit:

```turtle
<.../enumerations/{enumeration-id}/values/{position-token}>
  skos:inScheme <.../enumerations/{enumeration-id}> .
```

`skos:member` wird nicht fuer `skos:ConceptScheme` verwendet, weil `skos:member` formal zu `skos:Collection` passt. `skos:hasTopConcept` wird erst eingefuehrt, wenn Hierarchie oder Top-Concept-Semantik fachlich explizit modelliert wird. Die aktuellen Wertelisten sind flach; `skos:inScheme` reicht fuer die Scheme-Mitgliedschaft.

Multilinguale Labels werden auf Schemes und Values als `skos:prefLabel` publiziert. Aus praktischen Explorer-Gruenden wird derselbe Labelwert zusaetzlich als `rdfs:label` ausgegeben. `skos:notation` wird fuer vorhandene Codes oder den kanonischen Einzelwert verwendet. `rdf:value` wird nur fuer sicher erkennbare numerische oder boolesche Werte gesetzt.

## Versionierte Ressourcen-URIs

`Header.DictionaryUri` beschreibt den explizit zugeteilten Dictionary-Namespace. Vor einer Publikationsfreigabe bleibt dies eine neutrale `https://example.com/...`-URI. Eine LINDAS-URI wird erst nach einer manuellen Publikationsentscheidung eingetragen und muss dann die konkrete Version enthalten.

```text
https://lindas.admin.ch/fobl/kbob/dd-fm/{organization}/{dictionary-name}/{DictionaryVersion}/
```

Beispiel:

```text
https://lindas.admin.ch/fobl/kbob/dd-fm/ifma/data_dictionary_area_management/0.5.0/
```

Alle Klassen, Properties, Data Templates, Enumeration Schemes und Enumeration Values werden unter dieser versionierten Basis gemintet. SchemaForge verwendet eine absolute `DictionaryUri` unveraendert und haengt die Version nicht erneut an. Bei einer neutralen, unversionierten `example.com`-URI wird `DictionaryVersion` fuer lokale Vorabkonvertierungen einmalig angehaengt; ein solches Artefakt ist nicht fuer LINDAS freigegeben.

SchemaForge publiziert ausserdem zwei klar getrennte Dictionary-Knoten:

```turtle
<https://lindas.admin.ch/fobl/kbob/dd-fm/>
  a dcat:DatasetSeries ;
  dct:hasVersion <https://lindas.admin.ch/fobl/kbob/dd-fm/0.3.0/> .

<https://lindas.admin.ch/fobl/kbob/dd-fm/0.3.0/>
  a dcat:Dataset, dd:DataDictionary ;
  dct:isVersionOf <https://lindas.admin.ch/fobl/kbob/dd-fm/> ;
  dcat:inSeries <https://lindas.admin.ch/fobl/kbob/dd-fm/> ;
  owl:versionInfo "0.3.0" .
```

Der versionierte `Header.DictionaryUri` identifiziert die konkrete Publikation. SchemaForge leitet die zugehoerige unversionierte Serie durch Entfernen des abschliessenden SemVer-Segments ab. Ein spaeteres Release erhaelt eine neue freigegebene Versions-URI und ersetzt die bestehende Version nicht.

Eine i14y-URI ist keine Dictionary-Identitaet. SchemaForge erzeugt insbesondere keine i14y-URI aus dem Excel-Dateinamen. Falls ein bereits existierender i14y-Eintrag explizit als `Header.I14yDatasetUri` bereitgestellt wird, wird er ausschliesslich als `dcat:landingPage` am versionierten Dictionary publiziert. Fehlt dieses Metadatum, wird keine i14y-URI erfunden.

## URI-Strategie fuer Enumeration Values

Das Workbook besitzt derzeit keine expliziten stabilen IDs fuer einzelne Enumeration Values. Fuer das MVP werden Value-URIs deshalb deterministisch aus Enumeration-ID, Listenposition und kanonischem Wert-Token gebildet:

```text
.../enumerations/{Enumeration-ID}/values/{position}-{canonical-token}
```

Beispiel:

```text
https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/area-type-sia-416-code-enum/values/0001-1-2
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

<https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum>
  a skos:ConceptScheme, dd:EnumerationScheme ;
  skos:prefLabel "PredefinedType"@en, "Vordefinierter Typ"@de ;
  skos:notation "IFMA_V_31030000" ;
  dd:hasEnumerationValue
    <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum/values/0001-gfa>,
    <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum/values/0002-parking>,
    <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum/values/0003-userdefined> ;
  dct:source <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/> ;
  prov:wasDerivedFrom <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/> .

<https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum/values/0002-parking>
  a skos:Concept, dd:EnumerationValue, dd:AllowedValue ;
  skos:inScheme <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum> ;
  skos:prefLabel "PARKING"@en, "PARKING"@de ;
  skos:notation "PARKING" ;
  dd:enumerationPosition 2 ;
  dct:source <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/> .

<https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/properties/predefinedtype>
  a rdf:Property ;
  dd:usesEnumerationScheme <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum> ;
  dd:hasAllowedValue <https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/0.5.0/enumerations/predefinedtype-enum/values/0002-parking> .
```

## Alignment-Regeln

- `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch`, `skos:relatedMatch` fuer semantische Mappings verwenden.
- `qudt:hasUnit` nur fuer freigegebene QUDT-Unit-URIs verwenden.
- `dcterms:source` / `prov:wasDerivedFrom` fuer Provenienz verwenden.
- IFC-URIs als SSOT-Anker verwenden und niemals ueberschreiben.

## Design-Absicht

Dieses Vokabular ist bewusst minimal gehalten, damit ein schlank publiziertes Data Dictionary einfach abfragbar bleibt und dennoch ausreichend reichhaltig ist, um spaeter gegen IFC-abgeleitete RDF-Graphen validiert werden zu koennen.

## Data Templates und Property Requirements

Die `Data_Template`-Matrix wird als deskriptiver RDF-Layer publiziert. Alle Matrixzeilen mit derselben stabilen `DataTemplate-ID` werden zu einer `dd:DataTemplate`-Ressource aggregiert. Jede nicht-leere Property-Zelle wird zu einer eigenen `dd:PropertyRequirement`-Ressource.

Das Data Dictionary verknuepft seine Templates ueber `DataDictionary → dd:hasDataTemplate → DataTemplate`. Die fachliche Anwendbarkeit wird ausschliesslich in der Richtung `DataTemplate → dd:appliesToClass → Class` publiziert; eine inverse `Class → dd:hasDataTemplate → DataTemplate`-Kante wird nicht erzeugt.

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

Property-Grundmetadaten werden auf der allgemeinen Property publiziert:

```text
Property
  dd:datatype "BOOLEAN" ;
  dd:ifcDatatype "IfcBoolean" ;
  dd:status "..." ;
  qudt:hasUnit <QUDT-URI> .
```

Property Requirements koennen diese allgemeinen Werte im Data-Template-Kontext referenzieren oder, wo bereits publiziert, mit `dd:contextualDatatype` und `dd:contextualUnit` spiegeln. Unaufgeloeste Quelltext-Einheiten werden nicht als semantische QUDT-Einheit angezeigt.

### Matrixzellen

- Leere Zelle: keine `dd:PropertyRequirement`.
- `x`: Property ist im Data Template enthalten. Wenn die allgemeine Property ein Enumeration Scheme besitzt, wird `dd:usesEnumerationScheme` auf der Requirement-Ressource gesetzt und `dd:usesCompleteValueScheme true` publiziert.
- JSON-Liste, z. B. `["A", "B"]`: Property ist enthalten und auf eine Teilmenge der bestehenden Enumeration Values eingeschraenkt. Die Requirement-Ressource erhaelt `dd:usesCompleteValueScheme false` und je Wert ein `dd:allowedValue`.

Die allgemeine Property behaelt immer ihre vollstaendige Enumeration-Scheme-Verknuepfung. Requirement-Level-Values sind nur der kontextuelle Ausschnitt.

### Data-Template-URI-Strategie

Spalte B des Tabs `Data_Template` enthaelt die stabile `DataTemplate-ID`. Dieselbe ID wird ueber mehrere Zeilen wiederholt, wenn ein Data Template mehrere GoPs organisiert. Die URI lautet:

```text
.../data-templates/{data-template-id}
```

Beispiel:

```text
https://lindas.admin.ch/fobl/kbob/dd-fm/0.3.0/data-templates/gebaeude-dt
```

Die Identitaet bleibt beim Umsortieren oder Einfuegen von Zeilen stabil. Alle Zeilen mit derselben ID muessen dieselbe Class und dieselben Governance-Werte verwenden. Unterschiedliche LOIN-Angaben der aggregierten Zeilen werden als mehrere Werte am Data Template erhalten.

Property-Requirement-URIs liegen unter:

```text
.../property-requirements/{data-template-id}/{group-id-or-ungrouped}/{property-id}
```

### Groups of Properties

`GroupOfProperties` bleibt eine eigenstaendige Ressource. Jede Zeile kann null oder eine GoP referenzieren; ueber die wiederholte `DataTemplate-ID` werden daraus am Data Template `0..n` Kanten `dd:includesGroupOfProperties`. Die Singularform ist korrekt, weil jede RDF-Kante genau eine GoP als Objekt hat. Am Property Requirement wird der Zeilenkontext mit `dd:inGroupOfProperties` publiziert.

`Properties.IfcPropertySet (Pset) / IfcQuantitySet (Qto)` ist ausschliesslich IFC-Ausrichtungsmetadatum. Auch bei textlicher Uebereinstimmung mit einem GoP-Code wird daraus weder `dd:inGroupOfProperties` noch eine inverse GoP-Property-Kante inferiert.

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
