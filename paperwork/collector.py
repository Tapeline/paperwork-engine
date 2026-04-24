import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import dature
import frontmatter
from dature.metadata import Source

from paperwork.notes import KnowledgeBase, Note, Collection, TOC, TOCSection


@dataclass
class SingleNoteConfig:
    file: str
    assets: list[str] = field(default_factory=list)


@dataclass
class TOCSectionConfig:
    title: str
    toc: "TOCConfig"


type TOCConfig = list[SingleNoteConfig | TOCSectionConfig]


@dataclass
class CollectionConfig:
    title: str
    tags: list[str]
    abstract: str
    toc: list[SingleNoteConfig | TOCSectionConfig]


@dataclass
class KBConfig:
    name: str
    single_notes: list[SingleNoteConfig]
    collections: list[CollectionConfig]


class Collector:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def collect_kb(self) -> KnowledgeBase:
        kb_config = dature.load(
            Source(file_=self.base_dir / "paperwork-kb.yml"),
            KBConfig
        )
        single_notes = [
            self._collect_note(note)
            for note in kb_config.single_notes
        ]
        collections = [
            self._collect_collection(collection)
            for collection in kb_config.collections
        ]
        return KnowledgeBase(
            name=kb_config.name,
            single_notes=single_notes,
            collections=collections,
        )

    def _collect_note(self, note: SingleNoteConfig) -> Note:
        path = self.base_dir / note.file
        conf = frontmatter.load(str(path.absolute()))
        last_modified = os.path.getmtime(path)
        title = path.name.rsplit(".", maxsplit=1)[0]
        return Note(
            title=title,
            tags=conf.get("tags", []) or [],
            last_modified=datetime.fromtimestamp(last_modified),
            content_md=path.read_text(),
            loaded_assets_paths=[
                self.base_dir / asset for asset in note.assets
            ],
        )

    def _collect_collection(self, conf: CollectionConfig) -> Collection:
        def _walk_contents(toc: TOCConfig) -> TOC:
            contents = []
            for item in toc:
                match item:
                    case SingleNoteConfig() as note:
                        contents.append(self._collect_note(note))
                    case TOCSectionConfig() as section:
                        contents.append(
                            TOCSection(
                                section.title, _walk_contents(section.toc)
                            )
                        )
            return contents
        return Collection(
            title=conf.title,
            tags=conf.tags,
            abstract=conf.abstract,
            contents=_walk_contents(conf.toc)
        )
