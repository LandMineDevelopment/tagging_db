# Tagging System

A powerful CLI tool for tagging files with metadata, enabling efficient organization and search. Supports hybrid storage backends for flexibility and performance.

## Features

### Core Tagging
- **Add Tags**: `tag add <file> <tag1> <tag2>` – Assign multiple tags to files.
- **Remove Tags**: `tag remove <file> <tag>` – Remove specific tags.
- **List Tags**: `tag list <file>` or `tag list --all` – View tags on a file or all tags.
- **Rename Tags**: `tag rename <old> <new>` – Rename tags across all files.

### Search & Discovery
- **Find Files**: `tag find <query>` – Search by tags with regex/wildcard support.
- **Fuzzy Search**: `tag find <query> --fuzzy` – Typo-tolerant search using fuzzy matching.
- **Type Filtering**: Add `--type <ext>` to searches for file type-specific queries.

### Batch Operations
- **Apply Tags**: `tag apply <folder> <tag>` – Tag all files in a folder.
- **Type Filters**: Combine with `--type <ext>` for selective batch tagging.

### Advanced Features
- **Exclusions**: `tag exclude <tag1> <tag2>` – Prevent conflicting tags.
- **Undo**: `tag undo` – Revert the last operation.
- **Stats**: `tag stats` – View tag usage analytics.
- **Backend Switching**: `tag switch --to md/db` – Change storage backend.
- **Migration**: `tag switch --to md/db --migrate` – Transfer data between backends.

### Storage & Performance
- **Hybrid Storage**: Markdown (human-readable, portable) or SQLite DB (fast for large datasets).
- **Auto-Suggestions**: Contextual hints for tags and commands.
- **Tab Completion**: Shell completion for commands and paths (enable with `argcomplete`).
- **Configurable**: Custom separators, colors, storage paths via `.tagconfig`.

## Requirements
- Python 3.8+
- Dependencies: Click, SQLAlchemy, fuzzywuzzy, PyYAML, rich, tqdm, argcomplete

## Installation
1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy config example:
   ```bash
   cp .tagconfig.example .tagconfig
   ```
4. (Optional) Enable tab completion:
   ```bash
   eval "$(register-python-argcomplete main.py)"
   ```

## Usage Examples

### Basic Tagging
```bash
# Add tags to a file
python main.py add report.txt work project urgent

# Remove a tag
python main.py remove report.txt urgent

# List tags on a file
python main.py list report.txt

# List all tags
python main.py list --all
```

### Searching
```bash
# Find files with regex
python main.py find work/*

# Fuzzy search for typos
python main.py find wrk --fuzzy

# Filter by file type
python main.py find project --type txt
```

### Batch Operations
```bash
# Tag all PNG files in a folder
python main.py apply /photos image --type png

# Tag all files in a folder
python main.py apply /docs archive
```

### Advanced
```bash
# Set exclusions
python main.py exclude public confidential

# Undo last action
python main.py undo

# View stats
python main.py stats

# Switch to DB for performance
python main.py switch --to db --migrate
```

## Configuration
Edit `.tagconfig` (YAML) for customization:
```yaml
storage: md  # or 'db'
separator: /
colors:
  tag: green
exclusions: []
```

## Architecture
- **CLI Layer**: Click-based commands with auto-completion.
- **Engine**: Core logic with validation, exclusions, and undo.
- **Storage Abstraction**: Interfaces for MD and DB backends.
- **Config Management**: YAML-based settings persistence.

## Testing
Run tests with:
```bash
python -m pytest tests/
```

## Contributing
- Follow PEP8 style.
- Add tests for new features.
- Update README for changes.

## License
MIT License – Free to use and modify.