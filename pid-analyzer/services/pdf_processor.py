"""
PDF to image conversion for P&ID analysis.
Uses PyMuPDF (fitz) for high-quality rendering.
"""

import fitz  # PyMuPDF
import base64
from io import BytesIO
from typing import Tuple

from PIL import Image


class PDFProcessor:

    def pdf_to_image_base64(
        self,
        pdf_path: str,
        page_number: int = 0,
        dpi: int = 200,
    ) -> Tuple[str, str]:
        """
        Convert PDF page to base64 encoded image.

        Args:
            pdf_path: Path to PDF file
            page_number: Page to convert (0-indexed)
            dpi: Resolution for rendering

        Returns:
            Tuple of (base64_string, mime_type)
        """
        doc = fitz.open(pdf_path)

        if page_number >= len(doc):
            raise ValueError(
                f"Page {page_number} does not exist. PDF has {len(doc)} pages."
            )

        page = doc[page_number]

        # Render at high resolution
        zoom = dpi / 72  # 72 is default PDF DPI
        matrix = fitz.Matrix(zoom, zoom)

        pixmap = page.get_pixmap(matrix=matrix)

        img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

        buffer = BytesIO()
        img.save(buffer, format="PNG", quality=95)
        buffer.seek(0)

        base64_string = base64.b64encode(buffer.read()).decode("utf-8")

        doc.close()

        return base64_string, "image/png"

    def get_pdf_info(self, pdf_path: str) -> dict:
        """Get PDF metadata and page count."""
        doc = fitz.open(pdf_path)

        info = {
            "page_count": len(doc),
            "metadata": doc.metadata,
            "pages": [],
        }

        for i, page in enumerate(doc):
            info["pages"].append(
                {
                    "number": i,
                    "width": page.rect.width,
                    "height": page.rect.height,
                }
            )

        doc.close()

        return info
