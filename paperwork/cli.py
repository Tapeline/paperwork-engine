import os
import shutil
import sys
from pathlib import Path

import click

from paperwork.collector import Collector
from paperwork.exporter import Exporter


@click.command()
def paperwork_cli():
    click.echo("Paperwork v0.1.0")
    click.echo("Use --help.")


@click.group()
def paperwork_cli_group():
    """paperwork CLI."""


@paperwork_cli_group.command("export")
@click.argument(
    "project",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    default=""
)
@click.option(
    "-b", "--build-dir",
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    default="build"
)
def export_command(project: str, build_dir: str) -> None:
    collector = Collector(Path(project))
    kb = collector.collect_kb()
    click.echo(
        f"Collected {len(kb.single_notes)} notes, "
        f"{len(kb.collections)} collections in {kb.name}"
    )
    try:
        shutil.rmtree(build_dir)
    except FileNotFoundError:
        pass
    exporter = Exporter(Path(build_dir))
    exporter.export_kb(kb)
    click.echo(f"Exported to {Path(build_dir).absolute()}")


def main():
    if len(sys.argv) > 1:
        paperwork_cli_group()
    else:
        paperwork_cli()


if __name__ == '__main__':
    main()
