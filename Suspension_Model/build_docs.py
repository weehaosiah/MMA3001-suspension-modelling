"""Build portable HTML API documentation without running project experiments.

Run ``python build_docs.py`` from Suspension_Model, or from another directory
using this script's path. Among authored project files, only generated HTML is
written. Imports may create ignored Python/Matplotlib caches. Modules are imported
for their signatures and docstrings; no runner or model is called. Scientific
source content and saved results are left unchanged.
"""

import hashlib
import html
from html.parser import HTMLParser
import importlib
import importlib.util
import os
from pathlib import Path
import pydoc
import re
import sys
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parent
MODULE_NAMES = (
    "quarter_car", "run_nominal", "rk4_check", "verify_reduced_case",
    "run_verification", "dataset_design", "generate_dataset", "ml_development",
    "ml_plots", "ml_reference_check", "final_evaluation", "final_plots",
    "runtime_benchmark", "runtime_outputs", "profile_nominal", "profile_outputs", "build_docs",
)
PATH_NOTE = (
    "Portable display: <project> means the Suspension_Model directory. "
    "Displayed Path values, including ROOT/HERE and path defaults, abbreviate "
    "the absolute paths resolved at runtime; the Python values are unchanged. "
    "Dependency names without bundled pages are plain text."
)


def relative_url(target, folder):
    """Return a URL path relative to the page's folder."""
    return quote(Path(os.path.relpath(target, folder)).as_posix(), safe="/#")


class _PortableHTMLDoc(pydoc.HTMLDoc):
    """Retain pydoc signatures while removing machine-specific display paths."""

    def __init__(self, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination

    def filelink(self, url, path):
        """Link to the authored source using a relative path."""
        return ('<a href="' + relative_url(self.source, self.destination.parent) + '">'
                + html.escape(self.source.relative_to(ROOT).as_posix()) + '</a>')

    def repr(self, value):
        """Abbreviate runtime Path constants before pydoc truncates their text."""
        if isinstance(value, Path):
            try:
                suffix = value.relative_to(ROOT).as_posix()
            except ValueError:
                return html.escape("Path('<runtime path>')")
            text = "<project>" if suffix == "." else "<project>/" + suffix
            return html.escape("Path(" + repr(text) + ")")
        return super().repr(value)


def clean_page(page, destination, generated_paths):
    """Normalise signature paths and remove links to absent dependency pages."""
    # Function signatures use inspect's repr directly, bypassing HTMLDoc.repr.
    for path_text in (ROOT.as_posix(), str(ROOT), str(ROOT).replace("\\", "\\\\")):
        page = re.sub(re.escape(path_text), "&lt;project&gt;", page, flags=re.I)
    page = re.sub(r"(?:WindowsPath|PosixPath)\('(&lt;project&gt;[^']*)'\)", r"Path('\1')", page)

    def link(match):
        href = html.unescape(match.group(1))
        contents = match.group(2)
        if href == ".":
            index_url = relative_url(ROOT / "docs" / "index.html", destination.parent)
            return f'<a href="{index_url}">Documentation index</a>'
        parsed = urlsplit(href)
        if parsed.scheme:
            if parsed.scheme == "file":
                raise ValueError("Unexpected absolute source link in generated documentation.")
            return match.group(0)
        target = ((destination.parent / unquote(parsed.path)).resolve()
                  if parsed.path else destination.resolve())
        if target in generated_paths or target.exists():
            return match.group(0)
        return contents

    page = re.sub(r'<a href="([^"]*)"[^>]*>(.*?)</a>', link, page, flags=re.S)
    note = '<p class="portable-note">' + html.escape(PATH_NOTE) + '</p>\n'
    page = page.replace('<body>', '<body>\n' + note, 1)
    return "\n".join(line.rstrip() for line in page.splitlines()) + "\n"


class _PageLinks(HTMLParser):
    """Collect only local destinations and anchors for a documentation check."""

    def __init__(self):
        super().__init__()
        self.links = []
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "href" in attributes:
            self.links.append(attributes["href"])
        if "id" in attributes:
            self.anchors.add(attributes["id"])
        if tag == "a" and "name" in attributes:
            self.anchors.add(attributes["name"])


def validate_pages(pages):
    """Reject broken local paths/anchors or exposed absolute filesystem paths."""
    parsed = {}
    for path, page in pages.items():
        # Check decoded URLs as well as displayed text, including escaped paths.
        decoded = unquote(html.unescape(page))
        if re.search(r"(?:file:|(?<![A-Za-z])[A-Za-z]:[/\\]|/(?:Users|home)/)", decoded, re.I):
            raise ValueError(f"Absolute local path remains in {path.name}")
        parser = _PageLinks()
        parser.feed(page)
        parsed[path.resolve()] = parser
    count = 0
    for path, parser in parsed.items():
        for href in parser.links:
            uri = urlsplit(href)
            if uri.scheme:
                continue
            count += 1
            target = ((path.parent / unquote(uri.path)).resolve()
                      if uri.path else path)
            if target not in parsed and not target.exists():
                raise ValueError(f"Missing local link in {path.name}: {href}")
            if uri.fragment and target in parsed and uri.fragment not in parsed[target].anchors:
                raise ValueError(f"Missing local anchor in {path.name}: {href}")
    return count


def render_pages():
    """Render the explicit current modules; exclude historical failed runners."""
    specifications = [(name, ROOT / (name + ".py"), ROOT / "docs" / (name + ".html"))
                      for name in MODULE_NAMES]
    specifications.append(("review_saved", ROOT / "interpretation_v1" / "review_saved.py",
                           ROOT / "interpretation_v1" / "review_saved.html"))
    index = ROOT / "docs" / "index.html"
    generated_paths = {destination.resolve() for _, _, destination in specifications} | {index.resolve()}
    pages = {}
    for name, source, destination in specifications:
        if name == "review_saved":
            spec = importlib.util.spec_from_file_location(name, source)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        else:
            module = importlib.import_module(name)
        documenter = _PortableHTMLDoc(source, destination)
        page = documenter.page(name, documenter.document(module))
        pages[destination] = clean_page(page, destination, generated_paths)
    lines = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="utf-8">',
             '<title>Suspension model API documentation</title></head><body>',
             '<h1>Suspension model API documentation</h1>',
             '<p>API pages describe functions and their inputs. Start with the '
             '<a href="../README.md">project guide</a> for the physical explanation '
             'and reproducible workflows. Python source remains authoritative.</p>',
             '<p>Generated with <code>python build_docs.py</code>. No simulation, '
             'model fitting, prediction, or result audit is run while generating these pages.</p>',
             '<p>Among authored project files, only generated HTML is written. Imports '
             'may create ignored Python/Matplotlib caches. Scientific source content '
             'and saved results are left unchanged.</p>',
             '<p>' + html.escape(PATH_NOTE) + '</p>', '<ul>']
    for name, source, destination in specifications:
        lines.append(f'<li><a href="{relative_url(destination, index.parent)}">{name}</a>'
                     f' &mdash; <a href="{relative_url(source, index.parent)}">source</a></li>')
    lines += ['</ul>', '<p>The preserved failed preflight runner is historical evidence '
              'and is deliberately excluded from this current API index.</p>', '</body></html>', '']
    pages[index] = "\n".join(lines)
    return pages


def main():
    """Write repeatable HTML; imports may create ignored runtime caches."""
    pages = render_pages()
    links = validate_pages(pages)
    for destination, page in pages.items():
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(page, encoding="utf-8", newline="\n")
    fingerprint = hashlib.sha256("".join(
        path.relative_to(ROOT).as_posix() + "\n" + pages[path]
        for path in sorted(pages)).encode("utf-8")).hexdigest()
    print(f"Wrote {len(pages)} HTML pages; checked {links} local links and anchors.")
    print("No absolute local paths or file URLs remain.")
    print(f"Generated-content SHA256: {fingerprint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
