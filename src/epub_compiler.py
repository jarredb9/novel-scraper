"""EPUB generation and compilation module for the web novel scraper.

This module provides the EPUBCompiler class to compile sanitized novel chapters
into a standard EPUB format with Table of Contents navigation and CSS styling.
"""

import logging
import os
import uuid
from typing import List, Dict, Any, Optional
from ebooklib import epub
from src.utils import extract_chapter_number

logger = logging.getLogger("novel_scraper")

class EPUBCompiler:
    """Compiles sanitized chapter lists into a single EPUB document."""

    def __init__(
        self,
        output_path: str = "output.epub",
        title: str = "Compiled Novel",
        author: str = "Scraper",
    ):
        """Initializes the EPUB compiler.

        Args:
            output_path (str): Output file path for the compiled EPUB.
            title (str): Title of the book.
            author (str): Author/Creator of the book.
        """
        self.output_path = output_path
        self.title = title
        self.author = author

    def _chapter_sort_key(self, chapter: Dict[str, Any]):
        title = chapter.get("title", "")
        num = extract_chapter_number(title)
        return (num if num is not None else float("inf"), title)

    def _derive_identifier(
        self, source_url: Optional[str] = None
    ) -> str:
        """Derives a stable, unique EPUB identifier for a novel.

        Uses UUID5 (SHA-1 based) so the same input always produces
        the same identifier.  This lets e-reader apps recognise an
        updated EPUB as the same book and preserve reading position.

        Args:
            source_url: The novel's landing-page URL, if available.

        Returns:
            A deterministic URN string unique to this novel.
        """
        _ns = uuid.UUID("a4b1c2d3-e5f6-7890-abcd-ef1234567890")
        seed = source_url if isinstance(source_url, str) else self.title
        return f"urn:uuid:{uuid.uuid5(_ns, seed)}"

    def compile(
        self,
        chapters: List[Dict[str, Any]],
        cover_path: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> None:
        """Compiles a list of chapters into an EPUB file.

        Args:
            chapters (List[Dict[str, Any]]): List of dicts, each with keys
                'title' and 'paragraphs'.
            cover_path (Optional[str]): Path to the cover image to embed.
            source_url (Optional[str]): Landing page URL of the novel.
        """
        if not chapters:
            logger.warning("No chapters provided to compile.")
            return

        sorted_chapters = sorted(chapters, key=self._chapter_sort_key)

        book = epub.EpubBook()

        has_cover = False
        cover_page = None
        if cover_path and os.path.exists(cover_path):
            try:
                with open(cover_path, "rb") as f:
                    cover_content = f.read()
                book.set_cover(
                    "images/cover.jpg", cover_content, create_page=False
                )

                # Add custom cover XHTML page
                cover_page = epub.EpubHtml(
                    title="Cover", file_name="cover.xhtml", lang="en"
                )
                cover_page.content = """<html xmlns="http://www.w3.org/1999/xhtml"
xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>Cover</title>
    <style type="text/css">
        body {
            margin: 0;
            padding: 0;
            text-align: center;
            background-color: #ffffff;
        }
        img {
            max-width: 100%;
            max-height: 100%;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
</head>
<body>
    <div>
        <img src="images/cover.jpg" alt="Cover Image" />
    </div>
</body>
</html>"""
                book.add_item(cover_page)
                has_cover = True
            except Exception as e:
                logger.warning(f"Failed to embed cover in EPUB: {str(e)}")
                has_cover = False
        # Set metadata — use a stable, per-novel identifier so
        # readers recognise updated EPUBs as the same book.
        book_id = self._derive_identifier(source_url)
        book.set_identifier(book_id)
        book.set_title(self.title)
        book.set_language("en")
        book.add_author(self.author)
        if source_url and isinstance(source_url, str):
            book.add_metadata("DC", "source", source_url)

        # Style sheet content
        style_content = """
        @namespace epub "http://www.idpf.org/2007/ops";
        body {
            font-family: "Times New Roman", Times, serif;
            margin: 5%;
            line-height: 1.5;
        }
        h1 {
            text-align: center;
            margin-bottom: 2em;
        }
        p {
            text-indent: 1.5em;
            margin-bottom: 0.5em;
            margin-top: 0;
            text-align: justify;
        }
        """
        
        # Add CSS style sheet
        style_item = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style_content
        )
        book.add_item(style_item)

        epub_chapters = []
        for i, chapter in enumerate(sorted_chapters):
            title = chapter.get("title", f"Chapter {i+1}").strip()
            paragraphs = chapter.get("paragraphs", [])
            
            # Format paragraph text to HTML
            html_paragraphs = "".join(
                f"<p>{para.strip()}</p>"
                for para in paragraphs
                if para.strip()
            )
            
            # Construct EpubHtml chapter
            file_name = f"chap_{i}.xhtml"
            epub_chapter = epub.EpubHtml(
                title=title,
                file_name=file_name,
                lang="en",
                uid=f"chap_{i}"
            )
            
            # Set content with stylesheet link (omit xml declaration as it breaks get_body_content)
            epub_chapter.content = f"""<html xmlns="http://www.w3.org/1999/xhtml"
xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{title}</title>
    <link rel="stylesheet" href="style/nav.css" type="text/css" />
</head>
<body>
    <h1>{title}</h1>
    {html_paragraphs}
</body>
</html>"""
            
            # Link styling to the chapter
            epub_chapter.add_item(style_item)
            
            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)

        # Set table of contents
        book.toc = tuple(epub_chapters)

        # Create navigation files
        nav = epub.EpubNav()
        # Set content with child tag to prevent empty document parsing error
        # in ebooklib
        nav.content = '<html><body><h1>Table of Contents</h1></body></html>'
        book.add_item(nav)
        
        ncx = epub.EpubNcx()
        book.add_item(ncx)

        # Set spine (include nav first, or cover then nav)
        if has_cover and cover_page is not None:
            book.spine = [cover_page, "nav"] + epub_chapters
        else:
            book.spine = ["nav"] + epub_chapters

        # Ensure directory exists
        out_dir = os.path.dirname(self.output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Write EPUB
        epub.write_epub(self.output_path, book, {})
        print(f"EPUB successfully written to {self.output_path}")
        logger.info(f"EPUB successfully written to {self.output_path}")
