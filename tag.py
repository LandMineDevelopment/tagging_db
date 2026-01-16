"""
Tagging System CLI - Core implementation.
Use main.py for entry point.
"""

import click
from rich.console import Console
from typing import List
from tagging_db.config import ConfigManager
from tagging_db.engine import TagEngine
import argcomplete

console = Console()
app_config = ConfigManager()
config_path = '.tagconfig'
engine = TagEngine(app_config)

@click.group()
@click.option('--config', default='.tagconfig', help='Path to config file')
def cli(config):
    """Tagging system for files"""
    global app_config, config_path, engine
    config_path = config
    app_config.load(config)
    engine = TagEngine(app_config)

@cli.command()
@click.argument('file_path')
@click.argument('tags', nargs=-1)
def add(file_path: str, tags: List[str]) -> None:
    """Add tags to a file."""
    parsed_tags = [tuple(tag.split(':', 1)) if ':' in tag else (tag, '') for tag in tags]
    try:
        engine.add_tags(file_path, parsed_tags)
        console.print(f"[green]Added tags to {file_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        # Suggestions for existing tags
        all_tags = engine.get_all_tags()
        suggestions = [tag for tag in all_tags if any(t.lower() in tag.lower() for t in tags)][:3]
        if suggestions:
            console.print(f"[cyan]Similar tags: {', '.join(suggestions)}[/cyan]")

@cli.command()
@click.argument('query')
@click.option('--type', help='Filter by file type')
@click.option('--fuzzy', is_flag=True, help='Use fuzzy matching')
def find(query, type, fuzzy):
    """Search files by tags"""
    results = engine.search(query, type, fuzzy)
    for path, tags in results.items():
        console.print(f"{path}: {tags}")

    # Auto-suggestions: show close matches if no results
    if not results and not fuzzy:
        all_tags = engine.get_all_tags()
        suggestions = [tag for tag in all_tags if query.lower() in tag.lower()][:5]
        if suggestions:
            console.print(f"\n[cyan]Suggestions: {', '.join(suggestions)}[/cyan]")

@cli.command()
@click.argument('folder_path')
@click.argument('tag')
@click.option('--type', help='File type to apply to')
def apply(folder_path, tag, type):
    """Batch apply tag to folder"""
    parsed_tag = tag.split(':', 1) if ':' in tag else (tag, '')
    count = engine.batch_apply(folder_path, parsed_tag, type)
    console.print(f"[green]Applied to {count} files[/green]")

@cli.command()
@click.argument('file_path')
@click.argument('tags', nargs=-1)
def remove(file_path, tags):
    """Remove tags from a file"""
    parsed_tags = [tag.split(':', 1) if ':' in tag else (tag, '') for tag in tags]
    try:
        engine.remove_tags(file_path, parsed_tags)
        console.print(f"[green]Removed tags from {file_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.argument('file_path', required=False)
@click.option('--all', is_flag=True, help='List all tags')
def list(file_path, all):
    """List tags on a file or all tags"""
    if all:
        tags = engine.get_all_tags()
        console.print("All tags:", ', '.join(tags))
    elif file_path:
        tags = engine.get_tags(file_path)
        console.print(f"{file_path}: {tags}")
    else:
        console.print("[red]Specify --all or a file path[/red]")

@cli.command()
@click.argument('old_tag')
@click.argument('new_tag')
def rename(old_tag, new_tag):
    """Rename a tag across all files"""
    try:
        engine.rename_tag(old_tag, new_tag)
        console.print(f"[green]Renamed '{old_tag}' to '{new_tag}'[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
def stats():
    """Show tag statistics"""
    stats = engine.get_stats()
    console.print(f"Total tags: {stats['total_tags']}")
    console.print(f"Unique tags: {stats['unique_tags']}")
    console.print("Top tags:")
    for tag, count in stats['top_tags']:
        console.print(f"  {tag}: {count}")

@cli.command()
def undo():
    """Undo the last operation"""
    try:
        msg = engine.undo()
        console.print(f"[green]{msg}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option('--to', required=True, type=click.Choice(['md', 'db']))
@click.option('--migrate', is_flag=True, help='Migrate data to new backend')
def switch(to, migrate):
    """Switch storage backend"""
    global app_config, engine
    current = app_config.get('storage')
    if migrate and current != to:
        # Perform migration
        if to == 'db':
            from tagging_db.storage.database import DatabaseStorage
            new_storage = DatabaseStorage(app_config)
        else:
            from tagging_db.storage.markdown import MarkdownStorage
            new_storage = MarkdownStorage(app_config)
        
        # Get all data from current storage
        all_data = engine.storage.get_all_data()
        # Add to new storage
        for file_path, tags in all_data.items():
            new_storage.add_tags(file_path, [(tag, '') for tag in tags])
        
        console.print(f"[green]Migrated data to {to} storage[/green]")
    
    app_config.data['storage'] = to
    app_config.save(config_path)
    engine = TagEngine(app_config)
    console.print(f"[green]Switched to {to} storage[/green]")

if __name__ == '__main__':
    argcomplete.autocomplete(cli)
    cli()