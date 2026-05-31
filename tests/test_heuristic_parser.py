"""Unit tests for heuristic parsing fallback of web novel chapters."""

import pytest
from src.parser import XPathParser

def test_heuristic_title_h1():
    """Verify that title heuristic extracts first h1 tag."""
    html_content = """
    <html>
      <body>
        <div>Random Content</div>
        <h1>Chapter 123: H1 Title</h1>
        <h2>Chapter 123: H2 Title</h2>
        <div class="chapter-title">Wrong Title</div>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content)
    assert title == "Chapter 123: H1 Title"

def test_heuristic_title_h2_fallback():
    """Verify that title heuristic falls back to h2 tag."""
    html_content = """
    <html>
      <body>
        <div>Random Content</div>
        <h2>Chapter 123: H2 Title</h2>
        <div class="chapter-title">Wrong Title</div>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content)
    assert title == "Chapter 123: H2 Title"

def test_heuristic_title_class_fallback():
    """Verify that title heuristic falls back to element with class containing 'title'."""
    html_content = """
    <html>
      <body>
        <div>Random Content</div>
        <div class="main-title-container">Chapter 123: Class Title</div>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content)
    assert title == "Chapter 123: Class Title"

def test_heuristic_title_tag_fallback():
    """Verify that title heuristic falls back to <title> tag with cleanup."""
    html_content = """
    <html>
      <head><title>Chapter 123: HTML Title - FreeWebNovel</title></head>
      <body>
        <div>Random Content</div>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content)
    assert title == "Chapter 123: HTML Title"

def test_heuristic_body_p_density():
    """Verify that body heuristic selects container with highest p-tag density."""
    html_content = """
    <html>
      <body>
        <h1>Chapter Title</h1>
        <div class="header">
          <p>Some header text</p>
        </div>
        <div class="main-content">
          <p>Paragraph 1 of main story.</p>
          <p>Paragraph 2 of main story.</p>
          <p>Paragraph 3 of main story.</p>
        </div>
        <div class="footer">
          <p>Footer p</p>
        </div>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content)
    assert "Paragraph 1 of main story." in body
    assert "Paragraph 2 of main story." in body
    assert "Paragraph 3 of main story." in body
    assert "Footer p" not in body

def test_heuristic_body_raw_fallback():
    """Verify that body heuristic falls back to raw elements/text/breaks if p tags are absent."""
    html_content = """
    <html>
      <body>
        <h1>Chapter 123</h1>
        <article class="content">
          Line 1 of raw text.<br/>
          Line 2 of raw text.<br/>
        </article>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content)
    assert "Line 1 of raw text." in body
    assert "Line 2 of raw text." in body
