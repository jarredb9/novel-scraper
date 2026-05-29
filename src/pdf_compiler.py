import os
import logging
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas

logger = logging.getLogger("novel_scraper")

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that tracks and draws page numbers in the footer."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        # Draw page numbers at the very end when all pages are generated
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 9)
        # Check if we should draw page number (starting after the TOC page)
        # For basic flow, let's check if the page number is greater than 1
        if self._pageNumber > 1:
            page_text = f"{self._pageNumber}"
            # Centered at bottom (0.5 inch from bottom = 36 points)
            width, height = letter
            self.drawCentredString(width / 2.0, 36, page_text)
        self.restoreState()


class PDFCompiler:
    """Compiles sanitized chapter lists into a single PDF document."""

    def __init__(self, output_path: str = "output.pdf"):
        """Initializes the PDF compiler.

        Args:
            output_path (str): Output file path for the compiled PDF.
        """
        self.output_path = output_path
        # 0.5 inches margin = 36 points
        self.margin = 36
        self.pagesize = letter

    def compile(self, chapters: List[Dict[str, Any]]) -> None:
        """Compiles a list of chapters into the PDF.

        Args:
            chapters (List[Dict[str, Any]]): A list of dicts, each with keys 'title' and 'paragraphs'.
        """
        if not chapters:
            logger.warning("No chapters provided to compile.")
            return

        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=self.pagesize,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin + 18,  # Extra space for page numbers in bottom margin
        )

        styles = getSampleStyleSheet()
        
        # Modify existing styles or define unique ones
        title_style = ParagraphStyle(
            name="ChapterTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceAfter=15,
            keepWithNext=True,
        )

        body_style = ParagraphStyle(
            name="ChapterBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,  # 1.5 equivalent leading (10pt font * 1.5 = 15pt leading)
            spaceAfter=8,
        )

        story = []

        # For basic layout: Add placeholder page for TOC (so numbering starts on page 2)
        # We add a placeholder first page that will become the TOC in the next task.
        story.append(Paragraph("Table of Contents Placeholder", title_style))
        story.append(Spacer(1, 20))
        story.append(PageBreak())

        # Compile each chapter
        for i, chapter in enumerate(chapters):
            title = chapter.get("title", f"Chapter {i+1}")
            paragraphs = chapter.get("paragraphs", [])

            # Add chapter heading
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 10))

            # Add body paragraphs
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, body_style))

            # Only append PageBreak if it's not the last chapter
            if i < len(chapters) - 1:
                story.append(PageBreak())

        # Build PDF using our custom NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info(f"Successfully compiled PDF to {self.output_path}")
