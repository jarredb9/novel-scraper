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
    """Custom canvas that tracks page numbers, registers bookmarks, and draws footers."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bookmark_map = {}

    def showPage(self):
        # Draw page number footer before showing page
        first_chap_page = 2
        for k, v in self.bookmark_map.items():
            if k == "chap_0":
                first_chap_page = v
                break
        
        if self._pageNumber >= first_chap_page:
            self.saveState()
            self.setFont("Helvetica", 9)
            page_text = f"{self._pageNumber}"
            width, height = letter
            self.drawCentredString(width / 2.0, 36, page_text)
            self.restoreState()

        super().showPage()

    def bookmarkPage(self, key, *args, **kwargs):
        super().bookmarkPage(key, *args, **kwargs)
        self.bookmark_map[key] = self._pageNumber


class BookmarkedParagraph(Paragraph):
    """Paragraph subclass that automatically creates a PDF bookmark and sidebar outline entry."""
    
    def __init__(self, text: str, style: ParagraphStyle, key: str, level: int = 0, *args, **kwargs):
        super().__init__(text, style, *args, **kwargs)
        self.key = key
        self.level = level

    def draw(self):
        super().draw()
        canvas = self.canv
        # Add bookmark destination on the canvas
        canvas.bookmarkPage(self.key)
        # Clean tags from text for clean outline representation
        clean_title = self.getPlainText().strip()
        canvas.addOutlineEntry(clean_title, self.key, level=self.level, closed=False)


class PDFCompiler:
    """Compiles sanitized chapter lists into a single PDF document with a clickable TOC and bookmarks."""

    def __init__(self, output_path: str = "output.pdf"):
        """Initializes the PDF compiler.

        Args:
            output_path (str): Output file path for the compiled PDF.
        """
        self.output_path = output_path
        self.margin = 36  # 0.5 inches in points
        self.pagesize = letter
        self.bookmark_map = {}

    def compile(self, chapters: List[Dict[str, Any]]) -> None:
        """Compiles a list of chapters into the PDF, stabilizing page numbers for the TOC.

        Args:
            chapters (List[Dict[str, Any]]): A list of dicts, each with keys 'title' and 'paragraphs'.
        """
        if not chapters:
            logger.warning("No chapters provided to compile.")
            return

        # Multi-pass page stabilization loop to handle dynamic TOC size
        max_passes = 5
        self.bookmark_map = {}

        for pass_num in range(max_passes):
            previous_map = dict(self.bookmark_map)
            
            # Reset temporary map during compilation of this pass
            current_map = {}

            def canvas_factory(*args, **kwargs):
                c = NumberedCanvas(*args, **kwargs)
                c.bookmark_map = current_map
                return c

            story = self._generate_story(chapters, pass_num)

            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=self.pagesize,
                leftMargin=self.margin,
                rightMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin + 18,
            )
            doc.build(story, canvasmaker=canvas_factory)

            # Store the updated page locations
            self.bookmark_map = current_map

            # Check if page locations have stabilized
            if self.bookmark_map == previous_map:
                logger.info(f"PDF layout and TOC page numbers stabilized after pass {pass_num + 1}.")
                break
        else:
            logger.warning("PDF layout did not fully stabilize but finished maximum passes.")

    def _generate_story(self, chapters: List[Dict[str, Any]], pass_num: int) -> List[Any]:
        """Generates the document flow list (story).

        Args:
            chapters (List[Dict[str, Any]]): List of chapters.
            pass_num (int): Current pass index.

        Returns:
            List[Any]: Document flowables.
        """
        styles = getSampleStyleSheet()

        # Styles
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
            leading=15,
            spaceAfter=8,
        )

        toc_title_style = ParagraphStyle(
            name="TOCTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            spaceAfter=20,
        )

        toc_item_style = ParagraphStyle(
            name="TOCItem",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
        )

        story = []

        # Bookmark target for the top of the Table of Contents
        toc_key = "table_of_contents"
        story.append(BookmarkedParagraph(f'<a name="{toc_key}"/>Table of Contents', toc_title_style, key=toc_key, level=0))
        story.append(Spacer(1, 15))

        # Build TOC page contents
        for i, chapter in enumerate(chapters):
            title = chapter.get("title", f"Chapter {i+1}").strip()
            key = f"chap_{i}"
            
            # Fetch target page number if known, otherwise placeholder
            page_num = self.bookmark_map.get(key, "--")
            
            # Calculate dots to align page numbers nicely. Assumes roughly 80 char width.
            # Max width is constrained, so we use dot leader formatting.
            dots_count = max(5, 75 - len(title))
            dots = "." * dots_count

            # HTML link syntax is supported inside Paragraph text
            toc_html = f'<a href="#{key}">{title}</a> {dots} {page_num}'
            story.append(Paragraph(toc_html, toc_item_style))

        story.append(PageBreak())

        # Build Chapters
        for i, chapter in enumerate(chapters):
            title = chapter.get("title", f"Chapter {i+1}").strip()
            paragraphs = chapter.get("paragraphs", [])
            key = f"chap_{i}"

            # Chapter heading with bookmark & outline inclusion
            story.append(BookmarkedParagraph(f'<a name="{key}"/>{title}', title_style, key=key, level=1))
            story.append(Spacer(1, 10))

            # Paragraph contents
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, body_style))

            if i < len(chapters) - 1:
                story.append(PageBreak())

        return story
