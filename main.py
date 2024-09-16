from docling.document_converter import DocumentConverter
# source = "https://arxiv.org/pdf/2206.01062" # PDF path or URL
source = "https://documents.cap.org/protocols/Breast.DCIS_4.4.0.0.REL_CAPCP.pdf"
converter = DocumentConverter()
doc = converter.convert_single(source)
print(doc.render_as_markdown())
