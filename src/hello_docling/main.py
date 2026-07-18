import os

from dotenv import load_dotenv

from docling.document_converter import DocumentConverter

load_dotenv()

source = os.environ["DOCLING_SOURCE_URL"]
converter = DocumentConverter()
result = converter.convert(source)

print(result.document.export_to_markdown())
