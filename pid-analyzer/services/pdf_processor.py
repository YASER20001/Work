"""
PDF to image conversion for P&ID analysis.
Uses PyMuPDF (fitz) for high-quality rendering.
Supports multi-page PDFs and high-DPI rendering for dense engineering drawings.
"""

import fitz  # PyMuPDF
import base64
from io import BytesIO
from typing import Tuple, List

from PIL import Image


class PDFProcessor:

    def pdf_to_image_base64(
        self,
        pdf_path: str,
        page_number: int = 0,
        dpi: int = 300,
    ) -> Tuple[str, str]:
        """
        Convert PDF page to base64 encoded image at high resolution.
        P&ID drawings are dense — 300 DPI is the minimum for accurate symbol reading.
        """
        doc = fitz.open(pdf_path)

        if page_number >= len(doc):
            raise ValueError(
                f"Page {page_number} does not exist. PDF has {len(doc)} pages."
            )

        page = doc[page_number]

        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

        # If the image is extremely large (>20MP), scale down to avoid API limits
        max_pixels = 20_000_000
        total_pixels = img.width * img.height
        if total_pixels > max_pixels:
            scale = (max_pixels / total_pixels) ** 0.5
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        base64_string = base64.b64encode(buffer.read()).decode("utf-8")
        doc.close()

        return base64_string, "image/png"

    def pdf_to_all_pages_base64(
        self,
        pdf_path: str,
        dpi: int = 300,
    ) -> List[Tuple[str, str]]:
        """Convert all PDF pages to base64 images."""
        doc = fitz.open(pdf_path)
        pages = []

        for i in range(len(doc)):
            page = doc[i]
            zoom = dpi / 72
            matrix = fitz.Matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

            max_pixels = 20_000_000
            total_pixels = img.width * img.height
            if total_pixels > max_pixels:
                scale = (max_pixels / total_pixels) ** 0.5
                new_w = int(img.width * scale)
                new_h = int(img.height * scale)
                img = img.resize((new_w, new_h), Image.LANCZOS)

            buffer = BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            pages.append((base64.b64encode(buffer.read()).decode("utf-8"), "image/png"))

        doc.close()
        return pages

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
