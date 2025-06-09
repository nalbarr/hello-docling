help:
	@echo make run
	@echo make run-custom
	@echo make clean
	@echo ""
	@echo make docling-show-plugins
	@echo make docling-pipeline-vlm

run: clean
	uv run main.py

run-custom: clean
	uv run custom.py

clean:
	rm -fr ./scratch

docling-run:
	docling  --to md --no-ocr

docling-show-plugins:
	docling --show-external-plugins

docling-pipeline-vlm:
	docling --pipeline vlm \
					--vlm-model smoldocling \
					--output ./scratch \
					https://arxiv.org/pdf/2206.01062
