import pytest
from src.sanitizer import ContentSanitizer

def test_sanitizer_basic():
    raw_html = "<div><p>Paragraph 1</p><p>Paragraph 2</p></div>"
    sanitizer = ContentSanitizer()
    paragraphs = sanitizer.sanitize(raw_html)
    assert len(paragraphs) == 2
    assert paragraphs[0] == "Paragraph 1"
    assert paragraphs[1] == "Paragraph 2"

def test_sanitizer_removes_ads_and_noise():
    raw_html = """
    <div>
      <p>Hello world.</p>
      <p>If you find any errors ( broken links, non-standard content, etc.. ), Please let us know <a href="#">report</a> so we can fix it as soon as possible.</p>
      <p>Visit freewebnovel.com for more chapters.</p>
      <div class="ads">Some advertisement</div>
      <p>Good chapter.</p>
    </div>
    """
    # Let's specify that the sanitizer should clean typical ad elements or standard boilerplate lines
    # For freewebnovel, boilerplate includes:
    # "If you find any errors...", "Please let us know...", "Visit freewebnovel.com..."
    sanitizer = ContentSanitizer()
    paragraphs = sanitizer.sanitize(raw_html)
    assert "Hello world." in paragraphs
    assert "Good chapter." in paragraphs
    assert not any("errors" in p for p in paragraphs)
    assert not any("freewebnovel" in p for p in paragraphs)
    assert not any("advertisement" in p for p in paragraphs)

def test_sanitizer_excess_whitespace():
    raw_html = "<p>   Hello    world.   \n  This is  spaced.  </p>"
    sanitizer = ContentSanitizer()
    paragraphs = sanitizer.sanitize(raw_html)
    assert len(paragraphs) == 1
    assert paragraphs[0] == "Hello world. This is spaced."

def test_sanitizer_empty():
    sanitizer = ContentSanitizer()
    assert sanitizer.sanitize("") == []
    assert sanitizer.sanitize("   ") == []

def test_sanitizer_custom_boilerplate():
    sanitizer = ContentSanitizer(boilerplate_patterns=["custom_pattern"])
    paragraphs = sanitizer.sanitize("<p>This is custom_pattern text</p><p>Keep this</p>")
    assert paragraphs == ["Keep this"]

def test_sanitizer_removes_bad_tags():
    raw_html = "<div><p><script>alert(1)</script>Keep <b>bold</b> <script>alert(1)</script>this <style>body{}</style>text<subtxt>watermark</subtxt></p></div>"
    sanitizer = ContentSanitizer()
    paragraphs = sanitizer.sanitize(raw_html)
    assert paragraphs == ["Keep bold this text"]

def test_sanitizer_fallback_splitlines():
    raw_html = "Line 1\nLine 2\nLine 3"
    sanitizer = ContentSanitizer()
    paragraphs = sanitizer.sanitize(raw_html)
    assert paragraphs == ["Line 1", "Line 2", "Line 3"]

def test_clean_text_empty():
    sanitizer = ContentSanitizer()
    assert sanitizer.clean_text("") == ""
    assert sanitizer.clean_text(None) == ""

def test_sanitizer_parse_exception(monkeypatch):
    from lxml import html as lxml_html
    def mock_fromstring(*args, **kwargs):
        raise Exception("Trigger fallback")
    monkeypatch.setattr(lxml_html, "fromstring", mock_fromstring)
    
    # This should trigger the exception block and fallback to fragment_fromstring
    sanitizer = ContentSanitizer()
    paragraphs = sanitizer.sanitize("<p>Text in fallback</p>")
    assert paragraphs == ["Text in fallback"]


def test_fuzzy_branding_removal():
    sanitizer = ContentSanitizer()
    
    # 1. Standalone branding paragraphs (exact & fuzzy)
    raw_html_1 = "<p>Stay connected through freewebnovel</p>"
    assert sanitizer.sanitize(raw_html_1) == []
    
    raw_html_2 = "<p>Stay connected through freewebnovel.</p>"
    assert sanitizer.sanitize(raw_html_2) == []
    
    raw_html_3 = "<p>Stay tuned with freewebnovel!</p>"
    assert sanitizer.sanitize(raw_html_3) == []

    raw_html_4 = "<p>Explore new worlds at freewebnovel</p>"
    assert sanitizer.sanitize(raw_html_4) == []

    # Test newly added branding templates
    assert sanitizer.sanitize("<p>Your journey continues on freewebnovel</p>") == []
    assert sanitizer.sanitize("<p>Your journey continues at freewebnovel</p>") == []
    assert sanitizer.sanitize("<p>Stay updated through freewebnovel.</p>") == []
    assert sanitizer.sanitize("<p>Read new chapters at freewebnovel!</p>") == []
    assert sanitizer.sanitize("<p>Find adventures at freewebnovel</p>") == []
    assert sanitizer.sanitize("<p>Explore stories on freewebnovel</p>") == []
    assert sanitizer.sanitize("<p>Continue your adventure with freewebnovel</p>") == []

    # 2. Branding text at the end of a sentence
    raw_html_5 = "<p>The beast roared. Stay connected through freewebnovel</p>"
    assert sanitizer.sanitize(raw_html_5) == ["The beast roared."]

    raw_html_6 = "<p>The wizard cast a spell. Stay tuned with freewebnovel.</p>"
    assert sanitizer.sanitize(raw_html_6) == ["The wizard cast a spell."]

    # 3. Non-branding sentences containing similar words (should NOT be removed)
    # E.g. "We must stay connected through our communication devices."
    raw_html_7 = "<p>We must stay connected through our communication devices.</p>"
    assert sanitizer.sanitize(raw_html_7) == ["We must stay connected through our communication devices."]

    raw_html_8 = "<p>She decided to stay in a hotel. Explore new worlds at the library.</p>"
    assert sanitizer.sanitize(raw_html_8) == ["She decided to stay in a hotel. Explore new worlds at the library."]

    # 4. Mashup / Run-on text without correct spacing or punctuation
    raw_html_9 = "<p>The sword clashed.Stay connected through freewebnovel</p>"
    assert sanitizer.sanitize(raw_html_9) == ["The sword clashed."]

    raw_html_10 = "<p>The sword clashed Stay connected through freewebnovel.</p>"
    assert sanitizer.sanitize(raw_html_10) == ["The sword clashed"]

    # 5. Experience and Discover (including newlines)
    assert sanitizer.sanitize("<p>Experience more tales on freewebnovel</p>") == []
    assert sanitizer.sanitize("<p>Discover exclusive\ntales on freewebnovel</p>") == []


