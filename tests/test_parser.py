import pytest
from src.parser import XPathParser

def test_parse_valid_chapter():
    html_content = """
    <html>
      <body>
        <div class="main">
          <div class="chapter-content">
            <div class="title">
              <span>Chapter 776: The Beginning</span>
            </div>
            <div class="body">
              <div class="txt">
                <p>This is paragraph 1.</p>
                <p>This is paragraph 2.</p>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    # Override XPaths for tests to match the fixture structure, or use the default ones if they match
    # Since default xpaths are `/html/body/div[3]/div[1]/div/div[1]/span` and `/html/body/div[3]/div[1]/div/div[5]/div[1]`
    # Let's create HTML that matches the exact paths
    html_content_default = """
    <html>
      <body>
        <div></div>
        <div></div>
        <div> <!-- div[3] -->
          <div> <!-- div[1] -->
            <div>
              <div> <!-- div[1] -->
                <span>Chapter 776: The Beginning</span>
              </div>
              <div></div>
              <div></div>
              <div></div>
              <div> <!-- div[5] -->
                <div> <!-- div[1] -->
                  <p>This is paragraph 1.</p>
                  <p>This is paragraph 2.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    parser = XPathParser()
    title, body = parser.parse(html_content_default)
    assert title == "Chapter 776: The Beginning"
    assert "This is paragraph 1." in body
    assert "This is paragraph 2." in body

def test_parse_missing_elements():
    html_content_missing = "<html><body></body></html>"
    parser = XPathParser()
    with pytest.raises(ValueError, match="Could not extract chapter title"):
        parser.parse(html_content_missing)

def test_parse_custom_xpaths():
    html = """
    <html>
      <head><title>Custom Title</title></head>
      <body>
        <article>Custom Body Content</article>
      </body>
    </html>
    """
    parser = XPathParser(
        title_xpath="/html/head/title",
        body_xpath="/html/body/article"
    )
    title, body = parser.parse(html)
    assert title == "Custom Title"
    assert "Custom Body Content" in body

def test_parse_empty_content():
    parser = XPathParser()
    with pytest.raises(ValueError, match="HTML content is empty."):
        parser.parse("")
    with pytest.raises(ValueError, match="HTML content is empty."):
        parser.parse("   ")

def test_parse_empty_title():
    html = """
    <html>
      <head><title></title></head>
      <body><article>Some content</article></body>
    </html>
    """
    parser = XPathParser(title_xpath="/html/head/title", body_xpath="/html/body/article")
    with pytest.raises(ValueError, match="Chapter title is empty."):
        parser.parse(html)

def test_parse_missing_body():
    html = """
    <html>
      <head><title>Title</title></head>
      <body></body>
    </html>
    """
    parser = XPathParser(title_xpath="/html/head/title", body_xpath="/html/body/article")
    with pytest.raises(ValueError, match="Could not extract chapter body."):
        parser.parse(html)

def test_parse_invalid_html(monkeypatch):
    from lxml import html as lxml_html
    def mock_fromstring(*args, **kwargs):
        raise Exception("Mock parse error")
    monkeypatch.setattr(lxml_html, "fromstring", mock_fromstring)
    parser = XPathParser()
    with pytest.raises(ValueError, match="Failed to parse HTML: Mock parse error"):
        parser.parse("<html></html>")

