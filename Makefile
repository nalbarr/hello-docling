help:
	@echo make init-env
	@echo make run
	@echo make run-custom
	@echo make test
	@echo make clean
	@echo ""
	@echo make docling-run
	@echo make docling-show-plugins
	@echo make docling-pipeline-vlm

init-env:
	cp .env.example .env

run: clean
	uv run python -m hello_docling.main

run-custom: clean
	uv run python -m hello_docling.custom

test:
	uv run pytest

clean:
	rm -fr ./scratch

docling-run:
	uv run docling --to md --no-ocr --output ./scratch ./inputs/2408.09869v5.pdf

docling-show-plugins:
	uv run docling --show-external-plugins

docling-pipeline-vlm:
	uv run docling --pipeline vlm \
					--vlm-model smoldocling \
					--output ./scratch \
					https://arxiv.org/pdf/2206.01062
