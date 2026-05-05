# Review Request: Step 5 — Phase 2 Table/Figure/Formula Parsing

## Ready for Review: YES

## What Was Implemented

Extended `DoclingDocumentParser` and `DocumentModel` to support parsing of:
- **Tables** — extracted from `doc.tables` with row/col counts and captions
- **Figures** — extracted from `doc.pictures` with dimensions and captions
- **Formulas** — extracted via `iterate_items()` filtering for FormulaItem

### New Dataclasses

| Dataclass | Fields |
|-----------|--------|
| `TableInfo` | rows, cols, caption, style |
| `FigureInfo` | width, height, caption |
| `FormulaInfo` | content, numbered, number |

### Files Changed

- `D:\AI\project\PaperNormAI\backend\app\infrastructure\docling\document_model.py`
- `D:\AI\project\PaperNormAI\backend\app\infrastructure\docling\parser.py`

## Verification

**Test on `temp.docx`:**
```
Paragraphs: 390
Tables: 6
Figures: 13
Formulas: 20
```

Richard Review: **PASSED** (no Must Fix issues)