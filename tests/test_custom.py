from docling.datamodel.base_models import InputFormat

from hello_docling.custom import get_parser_easyocr


def test_get_parser_easyocr_allowed_formats():
    converter = get_parser_easyocr()
    assert InputFormat.PDF in converter.allowed_formats
    assert InputFormat.DOCX in converter.allowed_formats
    assert InputFormat.HTML in converter.allowed_formats
