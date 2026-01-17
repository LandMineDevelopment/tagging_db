#!/usr/bin/env python
"""
Simple runner script for tagging-db
"""
from src.config import ConfigManager
from rich.console import Console

console = Console()

def main():
    import sys
    # Check for help or set_storage commands, skip the check
    if '--help' in sys.argv or '-h' in sys.argv or (len(sys.argv) > 1 and sys.argv[1] in ('set_storage', 'set-storage')):
        from src.tag import cli
        cli()
        return

    # Early config check
    app_config = ConfigManager()
    app_config.load('.tagconfig')
    try:
        app_config.get_storage_path()
    except ValueError:
        console.print("[red]No storage location set. Run 'tagg set_storage <path>' to set where tags will be stored.[/red]")
        return

    from src.tag import cli
    cli()

if __name__ == "__main__":
    main()
