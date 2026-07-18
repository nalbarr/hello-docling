import json
import logging
import time
from pathlib import Path

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    OcrMacOptions,
    PdfPipelineOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

_log = logging.getLogger(__name__)


def get_parser_easyocr():
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    doc_converter = (
        DocumentConverter(  # all of the below is optional, has internal defaults.
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
                InputFormat.ASCIIDOC,
                InputFormat.MD,
            ],  # whitelist formats, non-matching files are ignored.
            format_options={
                #InputFormat.PDF: PdfFormatOption(
                #    pipeline_cls=StandardPdfPipeline, backend=PyPdfiumDocumentBackend
                #),
                #InputFormat.DOCX: WordFormatOption(
                #    pipeline_cls=SimplePipeline  # , backend=MsWordDocumentBackend
                #),
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),              
            },
        )
    )
    return doc_converter
      

def main():
    logging.basicConfig(level=logging.INFO)

    doc_converter = get_parser_easyocr()

    filenames = ['./inputs/2408.09869v5.pdf']
    for filename in filenames:
        input_doc_path = filename

        start_time = time.time()
        conv_result = doc_converter.convert(input_doc_path)
        end_time = time.time() - start_time

        _log.info(f"Document converted in {end_time:.2f} seconds.")

    output_dir = Path("scratch")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_result.input.file.stem
        
    with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown())
        

if __name__ == "__main__":
    main()
