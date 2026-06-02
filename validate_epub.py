"""Utility script to validate a compiled EPUB file against the raw cache.

It checks:
1. If any branding text (e.g. 'freewebnovel') remains in the EPUB.
2. If any story paragraphs in the cache were accidentally omitted from the EPUB.
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple
from lxml import html
from src.sanitizer import ContentSanitizer
from src.parser import XPathParser
from tqdm import tqdm

EPUB_PATH = r"C:\Users\jarre\iCloudDrive\Books\TheLegendaryBeastMaster.epub"
CACHE_DIR = r"./cache"


def get_epub_spine_files(epub_path: str) -> List[Tuple[str, str]]:
    """Reads container.xml and content.opf to get HTML files in spine order.

    Returns:
        List of (zip_path, raw_html_content) tuples.
    """
    with zipfile.ZipFile(epub_path) as z:
        # 1. Read container.xml to locate the OPF file
        container_xml = z.read("META-INF/container.xml")
        root = ET.fromstring(container_xml)
        ns = {"ns": "urn:oasis:names:tc:opendocument:xmlns:container"}
        opf_path = root.find(".//ns:rootfile", ns).attrib["full-path"]

        # 2. Read content.opf
        opf_dir = "/".join(opf_path.split("/")[:-1])
        opf_content = z.read(opf_path)
        opf_root = ET.fromstring(opf_content)

        # Map item IDs to their zip paths
        manifest = {}
        for item in opf_root.findall(".//{*}item"):
            item_id = item.attrib.get("id")
            href = item.attrib.get("href")
            if item_id and href:
                full_href = f"{opf_dir}/{href}" if opf_dir else href
                manifest[item_id] = full_href

        # Retrieve spine files in order
        spine_files = []
        for itemref in opf_root.findall(".//{*}itemref"):
            idref = itemref.attrib.get("idref")
            if idref in manifest:
                full_path = manifest[idref]
                if full_path.endswith((".html", ".xhtml", ".htm")):
                    spine_files.append((full_path, z.read(full_path).decode("utf-8", errors="ignore")))
        return spine_files


def extract_plain_text(html_content: str) -> str:
    """Extracts plain text content from HTML/XHTML, ensuring block elements have spaces."""
    try:
        tree = html.fromstring(html_content.encode("utf-8"))
        # Insert a space tail to all block elements to prevent text run-ons
        for elem in tree.xpath("//p | //div | //br | //li | //h1 | //h2 | //h3 | //h4 | //h5 | //h6"):
            if elem.tail:
                elem.tail = " " + elem.tail
            else:
                elem.tail = " "
        return tree.text_content()
    except Exception:
        # Fallback regex-based tag stripper
        return re.sub(r"<[^>]+>", " ", html_content)


def normalize(text: str) -> str:
    """Normalizes text to lowercase alphanumeric for robust substring matching."""
    return "".join(c for c in text.lower() if c.isalnum())


def main():
    if not os.path.exists(EPUB_PATH):
        print(f"Error: EPUB file not found at {EPUB_PATH}")
        return

    print("Reading EPUB spine...")
    try:
        epub_files = get_epub_spine_files(EPUB_PATH)
    except Exception as e:
        print(f"Error reading EPUB: {e}")
        return

    print(f"Found {len(epub_files)} text documents in EPUB.")

    # Cache pre-processed plain text versions of EPUB files
    epub_chapters = []
    for path, raw_content in epub_files:
        plain_text = extract_plain_text(raw_content)
        normalized_text = normalize(plain_text)
        epub_chapters.append({
            "path": path,
            "text": plain_text,
            "normalized": normalized_text
        })

    # Scan the cache directory for chapter HTML files
    print("Scanning cache directory...")
    cache_files = []
    if os.path.exists(CACHE_DIR):
        for f in os.listdir(CACHE_DIR):
            if f.startswith("chapter_") and f.endswith(".html"):
                match = re.search(r"chapter_(\d+)\.html", f)
                if match:
                    cache_files.append((int(match.group(1)), os.path.join(CACHE_DIR, f)))
    cache_files.sort()

    if not cache_files:
        print(f"No cached chapters found in {CACHE_DIR}")
        return

    print(f"Found {len(cache_files)} cached chapters. Starting validation...")

    parser = XPathParser()
    sanitizer = ContentSanitizer()
    missing_paragraphs_count = 0
    leftover_branding_count = 0
    matched_chapters_count = 0

    for ch_num, cache_path in tqdm(cache_files, desc="Validating Chapters"):
        with open(cache_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()

        # Extract only the body using XPathParser first (mirroring orchestrator.py)
        try:
            _, raw_body = parser.parse(raw_html)
        except Exception as e:
            tqdm.write(f"Error parsing Cache Chapter {ch_num}: {e}")
            continue

        # Sanitize cache content to extract what should be in the book
        sanitized_paras = sanitizer.sanitize(raw_body)
        if not sanitized_paras:
            continue

        # Find the matching EPUB document
        # We search by matching the normalized content of the first few long paragraphs
        fingerprints = [normalize(p) for p in sanitized_paras if len(p) > 40][:2]
        if not fingerprints:
            fingerprints = [normalize(p) for p in sanitized_paras if len(p) > 10][:2]

        matched_epub = None
        for ec in epub_chapters:
            if all(fp in ec["normalized"] for fp in fingerprints):
                matched_epub = ec
                break

        if not matched_epub:
            # Fallback: check if the string "Chapter X" or "X" exists as a strong match
            for ec in epub_chapters:
                if f"chapter{ch_num}" in ec["normalized"]:
                    matched_epub = ec
                    break

        if not matched_epub:
            tqdm.write(f"Warning: Could not align Cache Chapter {ch_num} with any EPUB document.")
            continue

        matched_chapters_count += 1

        # Check 1: Did we leave any freewebnovel branding in the EPUB chapter?
        # We search the plain text of the EPUB file
        leftover_branding = re.findall(r"\b\w*freewebnovel\w*\b", matched_epub["text"], re.IGNORECASE)
        if leftover_branding:
            tqdm.write(f"[LEFTOVER BRANDING] Chapter {ch_num} ({matched_epub['path']}): {set(leftover_branding)}")
            leftover_branding_count += len(leftover_branding)

        # Check 2: Were any sanitized paragraphs from the cache omitted from the EPUB?
        for i, para in enumerate(sanitized_paras):
            norm_para = normalize(para)
            if not norm_para:
                continue

            if norm_para not in matched_epub["normalized"]:
                # Print the warning
                tqdm.write(f"[MISSING CONTENT] Chapter {ch_num}: Paragraph {i+1} is missing from EPUB!")
                tqdm.write(f"  Cache Paragraph: {para[:120]}...")
                missing_paragraphs_count += 1

    print("\n" + "="*40)
    print("Validation Summary:")
    print(f"  Successfully matched chapters: {matched_chapters_count}")
    print(f"  Leftover branding instances:    {leftover_branding_count}")
    print(f"  Missing story paragraphs:      {missing_paragraphs_count}")
    print("="*40)


if __name__ == "__main__":
    main()
