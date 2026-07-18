# Upgrade Plan: docling 2.36.1 → 2.113.0

Generated 2026-07-18. Current repo pins `docling>=2.36.1`; latest release on
[docling-project/docling](https://github.com/docling-project/docling) is
**v2.113.0** (2026-07-14, confirmed via GitHub API and PyPI). This is a large
jump (~77 releases) spanning several internal reorganizations. This plan
covers what breaks in this repo and how to fix it.

## 1. Dependency bump

- `pyproject.toml`: bump `docling>=2.36.1` → `docling>=2.113.0` (or `>=2.113.0,<3.0.0`).
- `requirements.txt`: same bump.
- Python requirement unaffected: docling now requires `>=3.10,<4.0`; repo's
  `.python-version` (3.11.8) and `pyproject.toml` (`>=3.11.8`) are already
  compatible — no change needed.
- Regenerate `uv.lock` after bumping (`uv lock` / `uv sync`).
- Re-check `mlx-vlm>=0.1.27` still resolves alongside the new docling pin
  (docling's VLM/MLX-related extras have shifted — see §4).

## 2. Breaking change: OCR option classes moved (`custom.py`)

`custom.py` imports OCR option classes from per-engine model modules that no
longer exist at those paths:

```python
from docling.models.ocr_mac_model import OcrMacOptions
from docling.models.tesseract_ocr_cli_model import TesseractCliOcrOptions
from docling.models.tesseract_ocr_model import TesseractOcrOptions
```

As of the current release, `OcrMacOptions`, `TesseractCliOcrOptions`, and
`TesseractOcrOptions` (along with `EasyOcrOptions`, `RapidOcrOptions`,
`NemotronOcrOptions`, `OcrAutoOptions`, `KserveV2OcrOptions`) live in
**`docling.datamodel.pipeline_options`**. The OCR engine implementations
themselves now live under `docling.models.factories.ocr_factory` /
`docling.models.plugins`, not as flat top-level modules.

**Fix:** update the imports to:

```python
from docling.datamodel.pipeline_options import (
    OcrMacOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
```

These classes aren't actually used elsewhere in `get_parser_easyocr()` (only
imported), so this is a straightforward import fix. Confirm the rest of the
file — `PdfPipelineOptions`, `do_ocr`, `do_table_structure`,
`table_structure_options.do_cell_matching`, `DocumentConverter`,
`PdfFormatOption`, `WordFormatOption`, `InputFormat`, `SimplePipeline`,
`StandardPdfPipeline`, and `PyPdfiumDocumentBackend` — all still resolve at
their current paths (verified against `main` branch source tree), so no
other import changes are required.

## 3. Verify legacy `DoclingDocument` removal doesn't affect this repo

Release v2.103.0 says *"Remove the legacy DoclingDocument."* Neither
`main.py` nor `custom.py` references a legacy/v1 document model directly
(both only call `result.document.export_to_markdown()`), so this should be a
non-issue, but re-run both scripts after upgrading to confirm output is
unchanged.

## 4. Makefile review (target-by-target, against current CLI)

Verified every target against the live `docling/cli/main.py` `convert`
command on the current release (flag names, defaults, and enum values below
are all confirmed from source, not assumed):

| Target | Command | Status |
|---|---|---|
| `help` | (echoes usage) | Fine, no docling calls — no change needed. |
| `run` | `uv run main.py` | Fine — depends only on the import fix already covered by §2/§3 via `docling.document_converter`. |
| `run-custom` | `uv run custom.py` | Needs the import fix in §2 before this will run. |
| `clean` | `rm -fr ./scratch` | Fine, no docling dependency. |
| `docling-run` | `docling --to md --no-ocr` | **Broken independent of the version bump.** `source` is a required positional `typer.Argument` in `convert` — this command has no input file/URL/directory at all and will just print the CLI help (or error) rather than convert anything. `--to md` and `--no-ocr` are themselves still valid flags. **Fix while touching this file:** add a source, e.g. `docling --to md --no-ocr ./inputs/2408.09869v5.pdf` (or accept a `FILE` make variable). |
| `docling-show-plugins` | `docling --show-external-plugins` | Flag still present (`show_external_plugins`, eager callback) — no change needed. |
| `docling-pipeline-vlm` | `docling --pipeline vlm --vlm-model smoldocling --output ./scratch <url>` | `--pipeline` accepts `ProcessingPipeline.VLM = "vlm"` — still valid. `--vlm-model smoldocling` — still a valid preset id (`VlmConvertOptions.list_preset_ids()`), though note the CLI's *default* changed from the old default to `granite_docling`; since this target passes `smoldocling` explicitly, that default shift doesn't affect it. `--output` still valid. No change required, but run it post-upgrade to confirm the MLX backend resolves correctly given the mlx-vlm pin (§1). |

**Action items from this review:**
1. Fix `docling-run` to actually pass a source file (pre-existing bug, unrelated to the version bump, but should be fixed alongside since we're touching the Makefile/CLI surface anyway).
2. No flag renames/removals affect `docling-show-plugins` or `docling-pipeline-vlm`.
3. Optional: `docling-run` could add `--output ./scratch` for consistency with `docling-pipeline-vlm` (currently it has no `--output`, so it writes to the CLI's default output dir `.`, cluttering the repo root instead of `scratch/`).
4. New `test` target added per §5 below, listed in `help`.

## 5. Restructure into `src/` + `tests/` layout with pytest

Separate from the docling version bump, but bundled into this same pass
since it touches the same entry points (`main.py`/`custom.py`) and the
`Makefile`.

**New layout:**

```
src/
  hello_docling/
    __init__.py
    main.py        # moved from repo root
    custom.py      # moved from repo root
tests/
  test_custom.py   # default unit test
inputs/
  2408.09869v5.pdf
pyproject.toml
requirements.txt
Makefile
```

**`pyproject.toml` changes:**
- Add a `[build-system]` section (`hatchling`) so `hello_docling` is
  installed as an importable package from `src/` — required for `tests/` to
  `import hello_docling.custom` cleanly instead of relying on path hacks.
- Add a `[tool.hatch.build.targets.wheel]` `packages = ["src/hello_docling"]`
  entry (src-layout).
- Add `pytest` as a dev dependency via `[dependency-groups] dev = ["pytest>=8.0.0"]`
  (uv's convention) so it's not shipped with the runtime deps.
- Add `[tool.pytest.ini_options]` with `testpaths = ["tests"]`.

**Default unit test (`tests/test_custom.py`):**
Keep it fast and offline — no model downloads, no network, no real
conversion. Assert on the converter's static configuration instead:

```python
from docling.datamodel.base_models import InputFormat

from hello_docling.custom import get_parser_easyocr


def test_get_parser_easyocr_allowed_formats():
    converter = get_parser_easyocr()
    assert InputFormat.PDF in converter.allowed_formats
    assert InputFormat.DOCX in converter.allowed_formats
```

(Exact assertions to be finalized against `DocumentConverter`'s public
attributes at implementation time — the goal is a smoke test that the
pipeline wiring in `custom.py` still constructs without error after the
docling upgrade in §1/§2, not an end-to-end conversion test.)

**Makefile changes:**
- Update `run` / `run-custom` targets to point at the new paths, e.g.
  `uv run src/hello_docling/main.py` / `uv run src/hello_docling/custom.py`
  (or `uv run python -m hello_docling.main` once packaged — preferred, since
  it exercises the installed package rather than a loose script path).
- Add a new `test` target: `uv run pytest`.
- Add `test` to the `help` target's listed commands.

```makefile
test:
	uv run pytest

help:
	@echo make run
	@echo make run-custom
	@echo make test
	@echo make clean
	...
```

Note: relative paths inside `main.py`/`custom.py` (`./inputs/...`,
`./scratch`) keep working after the move since `uv run` executes with the
repository root as the working directory, not the script's own directory —
no path changes needed inside the moved files themselves.

## 6. Add `docs/run_book.md`

Add a `docs/` folder with a single concise run book covering day-to-day
usage of the project post-upgrade/restructure. Not a design doc — a
practical "how do I actually run this" reference.

**`docs/run_book.md` contents:**
- **Setup**: `uv sync`, Python/uv version expectations (from `.python-version`
  / `pyproject.toml`).
- **Common commands**: table mapping each `Makefile` target (§4) to what it
  does and when to use it — `run`, `run-custom`, `test`, `clean`,
  `docling-run`, `docling-show-plugins`, `docling-pipeline-vlm`.
- **Project layout**: brief pointer to `src/hello_docling/` (§5) vs
  `inputs/` vs `scratch/` (generated, gitignored output) vs `tests/`.
- **Direct CLI usage**: a couple of raw `docling` CLI examples (converting a
  local file, converting a URL, switching OCR engines) beyond what the
  Makefile wraps, since `custom.py` demonstrates programmatic
  `DocumentConverter` construction with format allow-lists.
- **Troubleshooting**: known gotchas worth documenting up front — e.g. first
  run downloads model weights (slow/network-dependent), `mlx-vlm` is
  macOS/Apple-Silicon-oriented, `scratch/` is wiped by `make clean` before
  every `run`/`run-custom`.

Keep it short (skim-in-under-a-minute length) — this is a run book, not a
tutorial. Link out to the upstream
[docling docs](https://docling-project.github.io/docling/) rather than
duplicating them.

`README.md` currently just says "hello-docling" with no usage info — add a
one-line pointer from `README.md` to `docs/run_book.md` so it's discoverable.

## 7. Scan for other newly-available features worth adopting (optional)

Not required for the upgrade, but notable additions since 2.36.1 that this
repo could take advantage of if useful later:

- Native PowerPoint/Excel chart parsing as classified pictures (v2.111–2.113).
- DCLX export format (`--to dclx`) alongside markdown (v2.110+).
- PDF heading-level inference from bookmarks/ToC (v2.106/2.109).
- OpenDocument (ODF) backend support (v2.107).
- Structured error categorization / typed backend load errors (v2.107).
- Fast ASR backend and Whisper decoding option passthrough (v2.108–2.109).

These are out of scope for the version bump itself — call out separately if
the user wants them.

## 8. Execution checklist

1. Bump `docling` version in `pyproject.toml` and `requirements.txt`.
2. Fix the three OCR-option imports in `custom.py`.
3. Fix `docling-run` in the `Makefile` to pass an actual source (§4).
4. Move `main.py`/`custom.py` into `src/hello_docling/`, add `__init__.py`,
   add `[build-system]`/`[tool.hatch...]` packaging config to
   `pyproject.toml`, add `pytest` as a dev dependency (§5).
5. Add `tests/test_custom.py` with the default smoke test (§5).
6. Add the `test` Makefile target and update `run`/`run-custom`/`help` (§5).
7. Add `docs/run_book.md` and link it from `README.md` (§6).
8. `uv lock && uv sync` (or equivalent) to refresh `uv.lock`.
9. `make run` — verify `main.py` converts the sample PDF and writes markdown
   to `scratch/`.
10. `make run-custom` — verify `custom.py`'s EasyOCR-based converter still
    builds and converts `inputs/2408.09869v5.pdf` without import errors.
11. `make docling-run` — verify the fixed target actually converts a file now.
12. `make docling-pipeline-vlm` — verify the SmolDocling VLM pipeline still
    runs end-to-end.
13. `make docling-show-plugins` — sanity check CLI still reports plugins as
    expected.
14. `make test` — verify the new pytest suite passes.
15. Spot-check exported markdown for regressions (table cell duplication and
    markdown table-cell bugs were fixed in this range, so output may differ
    slightly/improve).
