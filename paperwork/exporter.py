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

from paperwork.notes import Note, Collection, TOC, TOCSection, KnowledgeBase


class Exporter:
    def __init__(self, build_dir: Path):
        self.jinja = jinja2.Environment(
            loader=PackageLoader("paperwork"),
            autoescape=False
        )
        self.single_note_template = self.jinja.get_template("single_note.html")
        self.collection_note_template = self.jinja.get_template(
            "collection_note.html"
        )
        self.collection_template = self.jinja.get_template("collection.html")
        self.collection_section_template = self.jinja.get_template("collection_section.html")
        self.homepage_template = self.jinja.get_template("homepage.html")
        self.search_template = self.jinja.get_template("search.html")
        self.build_dir = build_dir
        self.md = MarkdownIt()
        self.md.use(obsidian_callout_plugin)
        self.md.use(footnote_plugin)
        self.md.use(tasklists_plugin)

    def render_export(
        self, template: Template, context: dict[str, Any], path: Path
    ) -> None:
        rendered = template.render(**context)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)

    def export_kb(self, kb: KnowledgeBase) -> None:
        self.render_export(
            self.homepage_template, {"kb": kb}, self.build_dir / "index.html"
        )
        for collection in kb.collections:
            self.export_collection(collection)
        for note in kb.single_notes:
            self.export_single_note(note)

    def export_single_note(self, note: Note) -> None:
        html = self.md.render(note.content_md)
        self.render_export(
            self.single_note_template,
            {"content": html, "note": note},
            self.build_dir / ("quick_notes/" + note.title + ".html")
        )

    def export_collection_note(
        self, note: Note, collection: Collection, toc_prefix: list[str]
    ) -> None:
        html = self.md.render(note.content_md)
        toc_path = reduce(
            lambda a, b: a / b,
            map(_clean_name, toc_prefix),
            self._collection_path(collection)
        )
        self.render_export(
            self.collection_note_template,
            {
                "content": html,
                "collection": collection,
                "toc_prefix": toc_prefix,
                "toc_path": toc_path,
                "note": note,
            },
            toc_path / (note.title + ".html")
        )

    def export_collection(self, collection: Collection) -> None:
        def _walk(toc: TOC, prefix: list[str]):
            for item in toc:
                match item:
                    case Note() as note:
                        self.export_collection_note(note, collection, prefix)
                    case TOCSection() as section:
                        _walk(section.toc, [*prefix, section.title])
                        section_path = reduce(
                            lambda a, b: a / b,
                            map(_clean_name, prefix),
                            self._collection_path(collection)
                        )
                        self.render_export(
                            self.collection_section_template,
                            {
                                "section_prefix": prefix,
                                "section_path": section_path,
                                "section_name": section.title,
                                "toc": section.toc
                            },
                            section_path / "index.html",
                        )

        _walk(collection.contents, [])
        self.render_export(
            self.collection_template, {"collection": collection},
            self._collection_path(collection) / "index.html"
        )

    def _collection_path(self, collection: Collection) -> Path:
        return self.build_dir / _clean_name(collection.title)


def _clean_name(name: str) -> str:
    name = translit(name.replace(" ", "-"), reversed=True)
    return "".join(
        c for c in name if c in string.ascii_letters + string.digits + "_-"
    )
