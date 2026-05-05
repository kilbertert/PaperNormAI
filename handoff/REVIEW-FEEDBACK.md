# Review Feedback: Step 5 — Table/Figure/Formula Parsing Support

## Ready for Builder: YES (with Minor Observations)

## Verification Results

### 1. TableInfo, FigureInfo, FormulaInfo dataclasses — PROPERLY DEFINED

| Dataclass | Location | Fields | Default Values |
|-----------|----------|--------|----------------|
| `TableInfo` | Lines 89-96 | rows, cols, caption, style | All have defaults |
| `FigureInfo` | Lines 98-104 | width, height, caption | All have defaults |
| `FormulaInfo` | Lines 106-112 | content, numbered, number | All have defaults |

All three dataclasses are correctly defined with proper Optional types and default values.

### 2. DocumentModel fields — CORRECT

Lines 125-127 in `document_model.py`:
```python
tables: list[TableInfo] = field(default_factory=list)
figures: list[FigureInfo] = field(default_factory=list)
formulas: list[FormulaInfo] = field(default_factory=list)
```

Correct use of `field(default_factory=list)` — maintains backward compatibility.

### 3. DoclingDocumentParser._convert_to_document_model() Extraction

| Component | Lines | Status |
|-----------|-------|--------|
| Tables | 124-135 | Extracts rows, cols, caption, style from `docling_doc.tables` |
| Figures | 137-150 | Extracts width, height, caption from `docling_doc.pictures` |
| Formulas | 152-163 | Iterates `docling_doc.iterate_items()` filtering for FormulaItem |

### 4. Backward Compatibility — MAINTAINED

All new fields have default empty lists via `field(default_factory=list)`. Existing code that creates `DocumentModel()` without these fields will continue to work.

### 5. Must Fix Issues — NONE

No blocking issues found. Implementation is functional.

## Minor Observations (Non-Blocking)

### 1. Formula extraction uses string type comparison (lines 155)
```python
if type(sub_item).__name__ == 'FormulaItem':
```
Uses `type().__name__` instead of `isinstance()`. Works but fragile if docling types change. Consider:
```python
from docling_core.types.doc.document import FormulaItem
if isinstance(sub_item, FormulaItem):
```

### 2. No hasattr checks for optional docling attributes
The code assumes `doc.tables`, `doc.pictures`, and `doc.iterate_items()` exist. If docling version changes or certain document types lack these, extraction will fail silently or error. Consider adding defensive hasattr checks:
```python
if hasattr(docling_doc, 'tables'):
    for table_item in docling_doc.tables:
        ...
```

### 3. caption_text() method assumption
Lines 126 and 139 assume `caption_text` method exists:
```python
caption = table_item.caption_text(docling_doc) if hasattr(table_item, 'caption_text') else None
```
This is already guarded with hasattr — good.

### 4. Formula extraction nested loop efficiency
Lines 153-163 have nested iteration:
```python
for item_tuple in docling_doc.iterate_items():
    for sub_item in item_tuple:
```
This iterates all document items to find formulas. For large documents, this could be slow but is acceptable for now.

## Conclusion

Step 5 implementation is complete and functional. All dataclasses are properly defined, DocumentModel fields have correct defaults for backward compatibility, and extraction logic is sound. The minor observations are suggestions for defensive coding but do not block the implementation.
