#!/usr/bin/env python3
"""
Tagging System CLI
"""

import click
from rich.console import Console
from tagging_db.config import ConfigManager
from tagging_db.engine import TagEngine

console = Console()
app_config = ConfigManager()
engine = TagEngine(app_config)

@click.group()
@click.option('--config', default='.tagconfig', help='Path to config file')
def cli(config):
    """Tagging system for files"""
    global app_config, engine
    app_config.load(config)
    engine = TagEngine(app_config)

@cli.command()
@click.argument('file_path')
@click.argument('tags', nargs=-1)
def add(file_path, tags):
    """Add tags to a file"""
    parsed_tags = [tag.split(':', 1) if ':' in tag else (tag, '') for tag in tags]
    try:
        engine.add_tags(file_path, parsed_tags)
        console.print(f"[green]Added tags to {file_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.argument('query')
@click.option('--type', help='Filter by file type')
def find(query, type):
    """Search files by tags"""
    results = engine.search(query, type)
    for path, tags in results.items():
        console.print(f"{path}: {tags}")

@cli.command()
@click.argument('folder_path')
@click.argument('tag')
@click.option('--type', help='File type to apply to')
def apply(folder_path, tag, type):
    """Batch apply tag to folder"""
    parsed_tag = tag.split(':', 1) if ':' in tag else (tag, '')
    count = engine.batch_apply(folder_path, parsed_tag, type)
    console.print(f"[green]Applied to {count} files[/green]")

if __name__ == '__main__':
    cli()