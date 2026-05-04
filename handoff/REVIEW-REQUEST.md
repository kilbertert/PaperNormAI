# Review Request — Must Fix Issues (Richard Review)

## Ready for Review: YES

## What Was Fixed

### Fix 1: Corrections silently fail when no paragraph matches
**File**: `backend/app/infrastructure/docx/document_merger.py`

Added `MergeResult` dataclass with fields:
- `success: bool`
- `output_path: Optional[Path]`
- `applied_corrections: int`
- `failed_corrections: List[Dict]` — tracks each failed correction with original text, paragraph_index, and error

Both `_merge_with_ai_word_skill()` and `_merge_with_basic_replacement()` now return `MergeResult` with full failure tracking.

### Fix 2: paragraph_index hint is ignored in fallback path
**File**: `backend/app/infrastructure/docx/document_merger.py`

In `_merge_with_basic_replacement()`, before iterating all paragraphs:
1. Check if `paragraph_index` hint is provided
2. If within bounds, check if that specific paragraph matches context
3. If match found, apply replacement and continue to next correction
4. Only if target paragraph didn't match, fall back to full iteration

### Fix 3: AI-Word-Skill partial failure leaves document inconsistent
**File**: `backend/app/infrastructure/docx/document_merger.py`

Changed `merge()` to use temp file pattern:
1. Copy original to temp file in system temp directory
2. Operate on temp file (either via AI-Word-Skill or basic replacement)
3. On success: move temp file to final output location
4. On failure: delete temp file, return error result
5. `finally` block ensures temp file cleanup

### Fix 4: Partial failure handling regression (REGRESSION from Fix 3)
**File**: `backend/app/infrastructure/docx/document_merger.py`

Fixed regression where successful corrections were discarded when some failed:
- When `applied_corrections > 0` and `failed_corrections > 0`, the temp file is now kept and moved to output
- `success=False` indicates partial failure (not all corrections applied), but the document contains all successful corrections
- Only when `applied_corrections == 0` is the temp file deleted (true failure case)

## Files Changed

- `D:\AI\project\PaperNormAI\backend\app\infrastructure\docx\document_merger.py`