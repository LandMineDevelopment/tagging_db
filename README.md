# Tagging System

A powerful CLI tool for tagging files with metadata, enabling efficient organization and search. Supports hybrid storage backends for flexibility and performance.

## Features

### Core Tagging
- **Add Tags**: `tagging-db add <file> <tag1> <tag2>` – Assign multiple tags to files.
- **Remove Tags**: `tagging-db remove <file> <tag>` – Remove specific tags.
- **List Tags**: `tagging-db list <file>` or `tagging-db list --all` – View tags on a file or all tags.
- **Rename Tags**: `tagging-db rename <old> <new>` – Rename tags across all files.

### Search & Discovery
- **Find Files**: `tagging-db find <query>` – Search by tags with regex/wildcard support.
- **Fuzzy Search**: `tagging-db find <query> --fuzzy` – Typo-tolerant search using fuzzy matching.
- **Type Filtering**: Add `--type <ext>` to searches for file type-specific queries.

### Batch Operations
- **Apply Tags**: `tagging-db apply <folder> <tag>` – Tag all files in a folder.
- **Type Filters**: Combine with `--type <ext>` for selective batch tagging.

### Advanced Features
- **Exclusions**: `tagging-db exclude <tag1> <tag2>` – Prevent conflicting tags.
- **Undo**: `tagging-db undo` – Revert the last operation.
- **Stats**: `tagging-db stats` – View tag usage analytics.
- **Backend Switching**: `tagging-db switch --to md/db` – Change storage backend.
- **Migration**: `tagging-db switch --to md/db --migrate` – Transfer data between backends.

### Storage & Performance
- **Hybrid Storage**: Markdown (human-readable, portable) or SQLite DB (fast for large datasets).
- **Auto-Suggestions**: Contextual hints for tags and commands.
- **Tab Completion**: Shell completion for commands and paths (enable with `argcomplete`).
- **Configurable**: Custom separators, colors, storage paths via `.tagconfig`.

## Requirements
- Python 3.8+
- Dependencies: Click, SQLAlchemy, fuzzywuzzy, PyYAML, rich, tqdm, argcomplete

## Installation

### From PyPI (Recommended)
```bash
pip install tagging-db
```
This installs the `tagging-db` command globally.

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tagging-db.git
   cd tagging-db
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) For development:
   ```bash
   pip install -e .[dev]
   ```

4. Copy config example:
   ```bash
   cp .tagconfig.example .tagconfig
   ```

5. (Optional) Enable tab completion:
   ```bash
   eval "$(register-python-argcomplete tagging-db)"
   ```

## Usage Examples

### Basic Tagging
```bash
# Add tags to a file
tagging-db add report.txt work project urgent

# Remove a tag
tagging-db remove report.txt urgent

# List tags on a file
tagging-db list report.txt

# List all tags
tagging-db list --all
```

### Searching
```bash
# Find files with regex
tagging-db find work/*

# Fuzzy search for typos
tagging-db find wrk --fuzzy

# Filter by file type
tagging-db find project --type txt
```

### Batch Operations
```bash
# Tag all PNG files in a folder
tagging-db apply /photos image --type png

# Tag all files in a folder
tagging-db apply /docs archive
```

### Advanced
```bash
# Set exclusions
tagging-db exclude public confidential

# Undo last action
tagging-db undo

# View stats
tagging-db stats

# Switch to DB for performance
tagging-db switch --to db --migrate
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