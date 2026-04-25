import re
import shutil
import string
from functools import reduce
from os import PathLike
from pathlib import Path
from typing import Any

import jinja2
from jinja2 import PackageLoader, select_autoescape, Template
from markdown_it import MarkdownIt
from mdformat_obsidian.mdit_plugins import (
    footnote_plugin,
    obsidian_callout_plugin,
    tasklists_plugin,
)
from transliterate import translit

from paperwork.embed_plugin import obsidian_embed_plugin
from paperwork.math_interceptor import svg_math_plugin
from paperwork.notes import Note, Collection, TOC, TOCSection, KnowledgeBase


class Exporter:
    def __init__(self, kb_dir: Path, build_dir: Path):
        self.jinja = jinja2.Environment(
            loader=PackageLoader("paperwork"),
            autoescape=False
        )
        self.jinja.filters["clean_name"] = _clean_name
        self.single_note_template = self.jinja.get_template("single_note.html")
        self.collection_note_template = self.jinja.get_template(
            "collection_note.html"
        )
        self.collection_template = self.jinja.get_template("collection.html")
        self.collection_section_template = self.jinja.get_template(
            "collection_section.html"
        )
        self.homepage_template = self.jinja.get_template("homepage.html")
        self.search_template = self.jinja.get_template("search.html")
        self.build_dir = build_dir
        self.kb_dir = kb_dir

        # Markdown parser with plugins
        self.md = MarkdownIt()
        self.md.use(obsidian_callout_plugin)
        self.md.use(footnote_plugin)
        self.md.use(tasklists_plugin)
        self.md.use(obsidian_embed_plugin)
        self.md.use(svg_math_plugin)
        # Enable tables (markdown-it has table support built-in)
        self.md.enable("table")

        # Render static assets once

    def _render_static_assets(self) -> None:
        """Render style.css and script.js to build directory."""
        self.build_dir.mkdir(parents=True, exist_ok=True)
        # Render CSS
        style_tmpl = self.jinja.get_template("css/style.css")
        style_css = style_tmpl.render()
        (self.build_dir / "style.css").write_text(style_css)

        # Render JS
        script_tmpl = self.jinja.get_template("js/script.js")
        script_js = script_tmpl.render()
        (self.build_dir / "script.js").write_text(script_js)

    def render_export(
        self, template: Template, context: dict[str, Any], path: Path
    ) -> None:
        rendered = template.render(**context)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    def _add_heading_ids_and_toc(self, html: str) -> tuple[str, str]:
        """
        Add id attributes to h2-h6 headings and extract a TOC HTML snippet.
        Returns (modified_html, toc_html).
        """
        toc_items = []
        def repl(match):
            level = int(match.group(1))
            title = match.group(2).strip()
            # Generate anchor from title text
            anchor = _clean_name(title)
            toc_items.append((level, anchor, title))
            return f'<h{level} id="{anchor}">{title}</h{level}>'

        html = re.sub(r'<h([1-6])>([^<]+)</h\1>', repl, html)

        # Build TOC HTML as a nested list
        if not toc_items:
            return html, ''

        toc_html = '<ul class="pw-toc-tree">\n'
        for lvl, anchor, title in toc_items:
            indent = '  ' * (lvl - 1)
            toc_html += f'{indent}<li class="pw-toc-item" style="padding-left: {8*(lvl-1)}px"><a class="pw-toc-link" href="#{anchor}">{title}</a></li>\n'
        toc_html += '</ul>'

        return html, toc_html

    def export_kb(self, kb: KnowledgeBase) -> None:
        self._render_static_assets()
        # Homepage: static_root is "."
        self.render_export(
            self.homepage_template,
            {"kb": kb, "static_root": ".", "per_page_toc": ""},
            self.build_dir / "index.html"
        )
        for collection in kb.collections:
            self.export_collection(collection, kb)
        for note in kb.single_notes:
            self.export_single_note(note, kb)

    def export_single_note(self, note: Note, kb: KnowledgeBase) -> None:
        html = self.md.render(
            note.content_md, env={
                "media_paths": note.loaded_assets_paths,
            }
        )
        # Add heading ids and extract TOC
        html, per_page_toc = self._add_heading_ids_and_toc(html)

        if note.loaded_assets_paths:
            (self.build_dir / "quick_notes/assets").mkdir(
                parents=True, exist_ok=True
            )
        for asset in note.loaded_assets_paths:
            shutil.copy(
                self.kb_dir / asset,
                self.build_dir / "quick_notes/assets" / Path(asset).name
            )

        # Compute static_root for quick_notes pages: ".." to go back to root
        static_root = ".."

        self.render_export(
            self.single_note_template,
            {
                "content": html,
                "note": note,
                "kb": kb,
                "static_root": static_root,
                "per_page_toc": per_page_toc,
            },
            self.build_dir / ("quick_notes/" + note.title + ".html")
        )

    def export_collection_note(
        self, note: Note, collection: Collection, toc_prefix: list[str], kb: KnowledgeBase
    ) -> None:
        html = self.md.render(
            note.content_md, env={
                "media_paths": note.loaded_assets_paths,
            }
        )
        # Add heading ids and extract TOC
        html, per_page_toc = self._add_heading_ids_and_toc(html)

        toc_path = reduce(
            lambda a, b: a / b,
            map(_clean_name, toc_prefix),
            self._collection_path(collection)
        )
        if note.loaded_assets_paths:
            (toc_path / "assets").mkdir(parents=True, exist_ok=True)
        for asset in note.loaded_assets_paths:
            shutil.copy(
                self.kb_dir / asset,
                toc_path / "assets" / Path(asset).name
            )

        # Compute static_root: go up from toc_path depth
        depth = len(toc_prefix) + 1  # +1 for collection dir
        static_root = "/".join([".."] * depth) if depth > 0 else "."

        self.render_export(
            self.collection_note_template,
            {
                "content": html,
                "collection": collection,
                "toc_prefix": toc_prefix,
                "toc_path": toc_path.relative_to(self.build_dir),
                "section_name": toc_prefix[-1] if toc_prefix else collection.title,
                "note": note,
                "kb": kb,
                "static_root": static_root,
                "per_page_toc": per_page_toc,
            },
            toc_path / (note.title + ".html")
        )

    def export_collection(self, collection: Collection, kb: KnowledgeBase) -> None:
        def _walk(toc: TOC, prefix: list[str]):
            for item in toc:
                match item:
                    case Note() as note:
                        self.export_collection_note(note, collection, prefix, kb)
                    case TOCSection() as section:
                        _walk(section.toc, [*prefix, section.title])
                        section_path = reduce(
                            lambda a, b: a / b,
                            map(_clean_name, prefix),
                            self._collection_path(collection)
                        )
                        # Section index pages: no per-page TOC needed
                        depth = len(prefix) + 1
                        static_root = "/".join([".."] * depth) if depth > 0 else "."
                        self.render_export(
                            self.collection_section_template,
                            {
                                "section_prefix": prefix,
                                "section_name": section.title,
                                "toc_path": section_path.relative_to(
                                    self.build_dir
                                ),
                                "toc": section.toc,
                                "kb": kb,
                                "static_root": static_root,
                                "per_page_toc": "",
                            },
                            section_path / "index.html",
                        )

        _walk(collection.contents, [])

        # Collection index
        static_root = ".."  # one level up from collection dir
        self.render_export(
            self.collection_template,
            {
                "collection": collection,
                "kb": kb,
                "static_root": static_root,
                "per_page_toc": "",
            },
            self._collection_path(collection) / "index.html"
        )

    def _collection_path(self, collection: Collection) -> Path:
        return self.build_dir / _clean_name(collection.title)


def _clean_name(name: str) -> str:
    try:
        name = translit(name.replace(" ", "-"), reversed=True)
    except Exception:
        name = name.replace(" ", "-")
    return "".join(
        c for c in name if c in string.ascii_letters + string.digits + "_-"
    )
