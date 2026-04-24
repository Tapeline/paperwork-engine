import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Note:
    title: str
    tags: list[str]
    last_modified: datetime
    content_md: str
    loaded_assets_paths: list[Path]


@dataclass
class TOCSection:
    title: str
    toc: "TOC"


type TOC = list[Note | TOCSection]


@dataclass
class Collection:
    title: str
    abstract: str
    tags: list[str]
    contents: TOC


@dataclass
class KnowledgeBase:
    name: str
    collections: list[Collection]
    single_notes: list[Note]
