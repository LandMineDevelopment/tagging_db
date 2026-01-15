# Tagging System

A CLI tool for tagging files with metadata, supporting Markdown and database storage.

## Features
- Add/remove tags on files
- Search files by tags with regex support
- Batch tag operations with file type filters
- Analytics for tag insights and duplicates
- Hybrid storage: Markdown (default) or SQLite DB
- Cross-platform CLI with tab completion

## Requirements
- Python 3.8+
- Click, sqlite3, fuzzywuzzy

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
tag add file.txt work/project
tag find work/*
tag apply /photos .png image
```

## Architecture
- CLI: Click-based interface
- Storage: Abstract layer for MD/DB
- Engine: Core tagging logic
- Analytics: Insights module