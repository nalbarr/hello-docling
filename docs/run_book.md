# Run Book

Concise usage reference for `hello-docling`. For docling itself, see the
[upstream docs](https://docling-project.github.io/docling/).

## Setup

```
uv sync
```

Requires Python `>=3.11.8` (see `.python-version`) and [uv](https://docs.astral.sh/uv/).

## Common commands

| Command | What it does |
|---|---|
| `make run` | Runs `src/hello_docling/main.py` — converts a hardcoded URL to markdown, prints to stdout. |
| `make run-custom` | Runs `src/hello_docling/custom.py` — builds a `DocumentConverter` with an explicit format allow-list and EasyOCR-backed PDF pipeline, converts `inputs/2408.09869v5.pdf`, writes markdown to `scratch/`. |
| `make test` | Runs the pytest suite (`tests/`). |
| `make clean` | Removes `scratch/` (generated output). Runs automatically before `run`/`run-custom`. |
| `make docling-run` | Raw `docling` CLI: converts `inputs/2408.09869v5.pdf` to markdown with OCR disabled, output to `scratch/`. |
| `make docling-show-plugins` | Lists third-party docling plugins available (requires `--allow-external-plugins` to actually use them). |
| `make docling-pipeline-vlm` | Raw `docling` CLI: converts a remote PDF using the VLM pipeline with the `smoldocling` preset. |

## Project layout

- `src/hello_docling/` — the package. `main.py` (minimal example) and
  `custom.py` (EasyOCR pipeline with format allow-list).
- `inputs/` — sample input PDF(s) checked into the repo.
- `scratch/` — generated conversion output, gitignored, wiped by `make clean`.
- `tests/` — pytest suite.
- `docs/` — this file.

## Direct CLI usage

Beyond what the `Makefile` wraps, the `docling` CLI can be invoked directly:

```
# Convert a local file to markdown
docling --to md ./inputs/2408.09869v5.pdf

# Convert a remote URL
docling --to md https://arxiv.org/pdf/2206.01062

# Switch OCR engine (e.g. tesseract instead of the default)
docling --ocr-engine tesseract ./inputs/2408.09869v5.pdf
```

`src/hello_docling/custom.py` shows the equivalent programmatic setup —
constructing a `DocumentConverter` directly with `PdfPipelineOptions` and an
`allowed_formats` list, rather than going through the CLI.

## Troubleshooting

- **First run is slow**: docling downloads model weights (layout, table
  structure, OCR) on first use — this requires network access and can take
  a while. Subsequent runs use the local cache.
- **`mlx-vlm` is Apple Silicon-oriented**: the VLM pipeline targets are
  primarily useful on macOS with Apple Silicon; behavior on other platforms
  may differ or require a different VLM backend.
- **`scratch/` gets wiped**: `make run` and `make run-custom` both depend on
  `clean`, which deletes `scratch/` before every run — don't store anything
  there you want to keep.
