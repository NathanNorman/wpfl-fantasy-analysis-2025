"""Smoke tests for WPFL Fantasy Analysis HTML files."""

import glob
import os
from html.parser import HTMLParser


class HTMLValidator(HTMLParser):
    """Simple HTML validator that checks for well-formed structure."""

    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []
        self.void_elements = {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
        }

    def handle_starttag(self, tag, attrs):
        if tag not in self.void_elements:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag </{tag}> with no open tags")
        elif self.tag_stack[-1] != tag:
            self.errors.append(
                f"Mismatched tag: expected </{self.tag_stack[-1]}>, got </{tag}>"
            )
            # Try to recover by popping until we find a match
            while self.tag_stack and self.tag_stack[-1] != tag:
                self.tag_stack.pop()
            if self.tag_stack:
                self.tag_stack.pop()
        else:
            self.tag_stack.pop()


ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")


def get_html_files():
    """Return all HTML files in the project root."""
    return glob.glob(os.path.join(ROOT_DIR, "*.html"))


def test_html_files_exist():
    """At least one HTML file should exist in the project."""
    html_files = get_html_files()
    assert len(html_files) > 0, "No HTML files found in project root"


def test_html_files_are_not_empty():
    """All HTML files should have content."""
    for filepath in get_html_files():
        size = os.path.getsize(filepath)
        assert size > 0, f"{os.path.basename(filepath)} is empty"


def test_html_files_have_doctype():
    """All HTML files should start with a DOCTYPE declaration."""
    for filepath in get_html_files():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        assert content.lower().startswith("<!doctype html"), (
            f"{os.path.basename(filepath)} missing <!DOCTYPE html>"
        )


def test_html_files_parse_without_errors():
    """All HTML files should parse as valid HTML."""
    for filepath in get_html_files():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        validator = HTMLValidator()
        try:
            validator.feed(content)
        except Exception as e:
            raise AssertionError(
                f"{os.path.basename(filepath)} failed to parse: {e}"
            )


def test_html_files_have_title():
    """All HTML files should have a <title> element."""
    for filepath in get_html_files():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
        assert "<title>" in content and "</title>" in content, (
            f"{os.path.basename(filepath)} missing <title> element"
        )


def test_html_files_have_lang_attribute():
    """All HTML files should have a lang attribute on <html>."""
    for filepath in get_html_files():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
        assert 'lang="' in content or "lang='" in content, (
            f"{os.path.basename(filepath)} missing lang attribute on <html>"
        )
