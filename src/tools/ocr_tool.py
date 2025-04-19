from docling.document_converter import DocumentConverter
import tempfile
import os
from autogen_core.tools import FunctionTool


async def convert_pdf_to_markdown(pdf_bytes):
    """
    Converts a PDF file in bytes to text in Markdown format.

    Args:
        pdf_bytes: Bytes of the PDF file to be converted.

    Returns:
        str: Converted text in Markdown format.

    Raises:
        Exception: If there is an error in the document conversion.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_bytes)
        temp_path = temp_file.name

    try:
        converter = DocumentConverter()
        result = converter.convert(temp_path)
        return result.document.export_to_markdown()
    finally:
        os.unlink(temp_path)


# Create the tool instance
convert_pdf_tool = FunctionTool(
    name="convert_pdf_to_markdown",
    description="Convert a PDF file to Markdown text using OCR",
    func=convert_pdf_to_markdown,
)

# ? Testing snippet (commented out)
# with open("src/tools/pdfTeste.pdf", "rb") as f:
#     pdf_bytes = f.read()

# markdown = convert_pdf_to_markdown(pdf_bytes)
# print(markdown)
