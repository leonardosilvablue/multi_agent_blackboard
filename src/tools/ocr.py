from docling.document_converter import DocumentConverter
import tempfile
import os
from agents import function_tool

@function_tool
def convert_pdf_to_markdown(pdf_bytes):
    """Converte um arquivo PDF em bytes para texto no formato Markdown.

    Args:
        pdf_bytes: Bytes do arquivo PDF a ser convertido.

    Returns:
        str: Texto convertido no formato Markdown.

    Raises:
        Exception: Se houver erro na conversão do documento.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdf_bytes)
        temp_path = temp_file.name

    try:
        converter = DocumentConverter()
        result = converter.convert(temp_path)
        return result.document.export_to_markdown()
    finally:
        os.unlink(temp_path)


#? Trecho pra testar a funcao
# with open("src/tools/pdfTeste.pdf", "rb") as f:
#     pdf_bytes = f.read()

# markdown = convert_pdf_to_markdown(pdf_bytes)
# print(markdown)