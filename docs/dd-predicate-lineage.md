# Data Dictionary predicate lineage

Status: current implementation inventory for human review

Source inspected: `scripts/map_to_rdf.py`

Current namespace: `https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/`
Proposed future namespace: `https://schema.ld.admin.ch/data-dictionary/` (subject to governance approval)

This inventory started with 40 custom predicates. The current mapper emits 38: `groupContainsProperty` has been retired, and `sourceWorkbook` has been replaced by PROV/Dublin Core provenance. Retired rows remain visible below so the decision lineage is auditable. This is not yet a normative vocabulary specification.

Legend:

- **Direct** — emitted from a specific populated Strukturvorlage field.
- **Derived** — inferred or generated from workbook structure or another field.
- **Inverse** — reverse link generated alongside a forward relation.
- **Compatibility** — legacy duplicate of a standard or bSDD-aligned predicate.
- **Constant** — mapper-generated value not supplied by the workbook.

| # | Predicate | Strukturvorlage origin and creation condition | Current triple pattern | Kind / important note |
|---:|---|---|---|---|
| 1 | `alignedWithIfcPset` | `Properties.IfcPropertySet (Pset) / IfcQuantitySet (Qto)` is non-empty. | `Property → Pset URI or literal` | Direct compatibility mapping. The mapper also emits provisional `bsdd:PropertySet` with the source value. This alignment never creates DD GoP membership. |
| 2 | `allowedValue` | A non-empty `Data_Template` Property cell contains an override list rather than exactly `x`; every override must resolve through `Properties.EnumerationDesignation (EN)` to a value in `Values`. | `PropertyRequirement → EnumerationValue` | Derived contextual subset. Zero or more triples per requirement. |
| 3 | `appliesToClass` | A material `Data_Template` row resolves its column-A Class designation to `Classes`. | `DataTemplate → Class` and `PropertyRequirement → Class` | Derived. The same predicate is emitted for the template and every requirement generated from the row. |
| 4 | `contextualDatatype` | A Property selected in `Data_Template` has `Properties.DataType (Base Type)`. | `PropertyRequirement → datatype literal` | Derived copy from the selected Property; it is not a Data_Template-specific override. |
| 5 | `contextualUnit` | A Property selected in `Data_Template` has `Properties.QUDT URI`; otherwise the mapper falls back to `Properties.Units/Einheit/Unité/Unità`. | `PropertyRequirement → QUDT IRI or unit literal` | Derived copy. QUDT wins over the text unit. |
| 6 | `datatype` | `Properties.DataType (Base Type)` is populated. | `Property → datatype literal` | Direct. |
| 7 | `documentItemReference` | `Documents.DocumentItemReference` is populated. | `Document → item-reference literal` | Compatibility duplicate; the mapper also emits `bsdd:documentItemReference`. |
| 8 | `enumerationPosition` | For every parsed entry in a `Values` multilingual enumeration list. | `EnumerationValue → 1-based integer` | Derived from list order, not from a dedicated cell. |
| 9 | `enumerationSchemeForProperty` | `Properties.EnumerationDesignation (EN)` resolves to `Values.Designation (EN)`. | `EnumerationScheme → Property` | Generated inverse of `usesEnumerationScheme`. |
| 10 | `groupContainsProperty` | **Retired.** Previously emitted when Pset/Qto text happened to match a DD GoP ID/code. | — | Removed because an IFC Pset/Qto association is not evidence of Strukturvorlage GoP membership. |
| 11 | `hasAllowedValue` | `Properties.EnumerationDesignation (EN)` resolves to a `Values` scheme. | `Property → every EnumerationValue in the scheme` | Derived global/full value set. Distinct from contextual `allowedValue`. |
| 12 | `hasClass` | Every processed `Classes` row, whether `Class-ID` is supplied or generated. | `DataDictionary → Class` | Generated dataset membership. |
| 13 | `hasDataTemplate` | Every distinct stable `DataTemplate-ID` produces one DataTemplate. | `DataDictionary → DataTemplate` | Generated dictionary membership. Repeated rows with the same ID are aggregated. Class applicability is expressed only in the semantically accurate direction through `DataTemplate → appliesToClass → Class`. |
| 14 | `hasDocument` | Every processed `Documents` row, whether `Document-ID` is supplied or generated. | `DataDictionary → Document` | Generated membership and compatibility duplicate; `bsdd:hasDocument` is also emitted. |
| 15 | `hasEnumerationScheme` | Every processed `Values` row becomes an EnumerationScheme. | `DataDictionary → EnumerationScheme` | Generated dataset membership. |
| 16 | `hasEnumerationValue` | Every parsed item from the multilingual lists in one `Values` row. | `EnumerationScheme → EnumerationValue` | Derived containment. SKOS `inScheme` is also emitted in the opposite direction. |
| 17 | `hasGroupOfProperties` | Every processed `GroupOfProperties` row, whether `GoP-ID` is supplied or generated. | `DataDictionary → GroupOfProperties` | Generated dataset membership. |
| 18 | `hasProperty` | Every processed `Properties` row, whether `Property-ID` is supplied or generated. | `DataDictionary → Property` | Generated dataset membership. |
| 19 | `hasPropertyRequirement` | Every non-empty Property cell in a material `Data_Template` row creates a PropertyRequirement. | `DataTemplate → PropertyRequirement` | Derived containment. |
| 20 | `ifcDatatype` | `Properties.DataType (IFC)` is populated. | `Property → IFC datatype literal` | Direct. The object is currently a literal, not an IFC datatype IRI. |
| 21 | `ifcObjectEntity` | `Classes.IfcObject Entity` is populated and starts with `Ifc`. The mapper constructs the IFC 4.3 class IRI. | `Class → IFC class IRI` | Derived from `IfcObject Entity`, **not** from `Classes.IFC_URI`. |
| 22 | `ifcPredefinedType` | `Classes.IfcObject Entity` plus a populated `Classes.PredefinedType` other than `USERDEFINED`; the mapper constructs the predefined IFC class IRI. | `Class → IFC predefined-type IRI` | Derived. `skos:exactMatch` and `skos:broadMatch` are emitted alongside it. |
| 23 | `inGroupOfProperties` | A PropertyRequirement is created from a `Data_Template` row whose column-C GoP resolves to `GroupOfProperties`. | `PropertyRequirement → GroupOfProperties` | Contextual requirement membership only. It is no longer inferred globally from IFC Pset/Qto text. |
| 24 | `includesGroupOfProperties` | Each row sharing a stable `DataTemplate-ID` may provide one resolvable GoP in column C. The mapper aggregates the distinct GoPs. | `DataTemplate → GroupOfProperties` | Cardinality `0..n`. The singular predicate name is retained because each RDF triple has exactly one object; multiple triples express the plural collection. |
| 25 | `inclusionMarker` | Raw content of each non-empty `Data_Template` Property cell. | `PropertyRequirement → marker literal` | Direct matrix value: usually `x` or the serialized override-list text. |
| 26 | `loinMilestone` | In templates containing a `Data_Template` `LOIN` anchor: value in the `LOIN_Milestone` column. | `DataTemplate → milestone literal` | Direct, dynamically named predicate. The current empty v1.0.0 template has no LOIN block, while the KBOB publication workbook does. |
| 27 | `loinRole` | `Data_Template.LOIN_Role` when the LOIN block exists and the cell is populated. | `DataTemplate → role literal` | Direct, dynamically named predicate. |
| 28 | `loinUsecase` | `Data_Template.LOIN_UseCase` when the LOIN block exists and the cell is populated. | `DataTemplate → use-case literal` | Direct, dynamically named predicate. Current local name is `loinUsecase` because it is generated programmatically. |
| 29 | `referencesDocument` | Five origins: `Classes.RelatedDocumentName (EN)` or legacy `RelatedDocuments`; `GroupOfProperties.RelatedDocumentName (EN)`; `Values.RelatedDocumentName (EN)`; `Properties.RelatedDocumentName (EN)`; or a marked Document column in `Data_Template`. The reference must resolve to `Documents`. | Source resource → Document | Direct/derived compatibility relation. For Data_Template, it is emitted from both DataTemplate and every PropertyRequirement in that row. `bsdd:referencesDocument` is also emitted. |
| 30 | `referencesDocumentSection` | A Class, GoP, Value scheme, or Property supplies `RelatedDocumentItemReference`, but that value does **not** resolve in the selected Document's item set. | Source resource → unresolved item-reference literal | Compatibility fallback only. A valid item reference uses the bSDD `DocumentSection`/`referencesSection` pattern and does not emit this `dd:` predicate. |
| 31 | `requiredByTemplate` | Every PropertyRequirement generated from a non-empty `Data_Template` Property cell. | `Property → PropertyRequirement` | Generated inverse of `requiresProperty`. |
| 32 | `requirementLevel` | Every generated PropertyRequirement. | `PropertyRequirement → "included"` | Constant. No workbook field currently supplies another level. |
| 33 | `requirementOfDataTemplate` | Every PropertyRequirement generated from a non-empty `Data_Template` Property cell. | `PropertyRequirement → DataTemplate` | Generated inverse of `hasPropertyRequirement`. |
| 34 | `requiresProperty` | Every non-empty `Data_Template` Property cell resolves its row-2 header to one `Properties` entry. | `PropertyRequirement → Property` | Derived matrix relation. |
| 35 | `revision` | `Documents.Revision` is populated. | `Document → revision literal` | Direct. |
| 36 | `sourceWorkbook` | **Retired.** | — | Replaced by a `prov:Entity` source-workbook resource linked with `prov:wasDerivedFrom` and `dct:source`; its filename is `dct:identifier`. |
| 37 | `status` | Emitted from `Classes.Status`, `GroupOfProperties.Status`, `Documents.Status`, `Values.Status`, `Properties.Status`, and `Data_Template.Governance → Status`. | Class, GroupOfProperties, Document, EnumerationScheme, Property, or DataTemplate → status literal | One lifecycle meaning reused across an explicitly documented union of subject types. |
| 38 | `usesCompleteValueScheme` | A selected Data_Template Property has a linked EnumerationScheme. It is `true` when the matrix cell is exactly `x`; it is `false` when the cell supplies a validated subset/override list. | `PropertyRequirement → boolean` | Derived coverage flag. |
| 39 | `usesEnumerationScheme` | Two origins: (a) `Properties.EnumerationDesignation (EN)` resolves to a Values scheme; (b) a PropertyRequirement inherits that resolved scheme from its selected Property. | `Property → EnumerationScheme` or `PropertyRequirement → EnumerationScheme` | Direct resolution plus derived contextual reuse. |
| 40 | `valueOfProperty` | For every EnumerationValue in a scheme resolved through `Properties.EnumerationDesignation (EN)`. | `EnumerationValue → Property` | Generated inverse of global `hasAllowedValue`. |

## Important non-custom mappings

These workbook fields do not create one of the 40 custom predicates:

| Workbook source | Current RDF mapping |
|---|---|
| `Classes.IFC_URI` | Only when `Classes.IfcObject Entity` is absent: `Class skos:exactMatch IFC_URI`. When `IfcObject Entity` exists, the mapper constructs the IFC class URI from that field instead. |
| `Properties.IFC_URI` | `Property skos:exactMatch IFC_URI`. |
| `Properties.QUDT URI` | `Property qudt:hasUnit QUDT_URI`; also copied contextually to a PropertyRequirement via `qudt:hasUnit` and custom `contextualUnit`. |
| `ConceptRelation.RelationType` | A standard SKOS predicate when recognized; otherwise the supplied absolute predicate IRI. It does not automatically become a `dd:` predicate. |
| `Header.I14yDatasetUri` | When present: `DataDictionary dcat:landingPage I14yDatasetUri`. The active template family currently has no such Header row. |

## Review flags before canonical registration

The inventory exposes terms that should not automatically be migrated without semantic review:

1. bSDD use needs a strict boundary. Canonical IFC 4.3 entity alignment should use the official bSDD identifier IRIs. The long-standing preview vocabulary may be used only for explicitly provisional IFC-specific metadata such as `bsdd:PropertySet`; document relations and general DD semantics must not depend on it.
2. Generated inverses remain migration candidates: `enumerationSchemeForProperty`, `requiredByTemplate`, `requirementOfDataTemplate`, and `valueOfProperty`. Canonical source RDF can publish only the forward relation; APP1 and APP2 can present a user-friendly reversed direction without persisting inverse triples. `groupContainsProperty` has already been removed.
3. Multi-domain predicates are not automatically semantically overloaded. `status` and `usesEnumerationScheme` express one relation across several valid domain classes. `hasDataTemplate` is now restricted to `DataDictionary → DataTemplate`; Class applicability uses `DataTemplate → appliesToClass → Class` and no inverse Class link is published.
4. `sourceWorkbook` has been replaced by PROV/Dublin Core provenance.
5. `inclusionMarker` and `requirementLevel` remain review items. Recommended canonical rule: creation of a PropertyRequirement means inclusion; `usesCompleteValueScheme` plus `allowedValue` describes full versus subset enumeration use. Do not publish the raw matrix marker. If requirement levels are later introduced, model them as controlled concepts rather than a constant free-text `"included"` value.
6. `Classes.Status`, `GroupOfProperties.Status`, and stable DataTemplate `0..n` GoP aggregation are now implemented.
