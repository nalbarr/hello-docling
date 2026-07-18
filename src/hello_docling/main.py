from docling.document_converter import DocumentConverter
# source = "https://arxiv.org/pdf/2206.01062" # PDF path or URL
source = "https://www.cap.org/wp-content/uploads/2026/06/Breast.DCIS_4.5.0.1.REL_CAPCP.pdf?download=true"
converter = DocumentConverter()
result = converter.convert(source)

print(result.document.export_to_markdown())
