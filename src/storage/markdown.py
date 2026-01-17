"""
Markdown-based storage backend for tags.
Stores data in a human-readable MD file.
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
from .interfaces import StorageInterface

class MarkdownStorage(StorageInterface):
    """Storage implementation using Markdown file."""
    
    def __init__(self, config):
        self.config = config
        self.tags_file = Path(config.get('tags_file', 'tags.md'))
        if not self.tags_file.exists():
            self._init_file()
    
    def _init_file(self) -> None:
        """Initialize the tags.md file with structure."""
        self.tags_file.write_text(
            "# Tagging System Data\n\n"
            "## Files and Tags\n\n"
            "## Tag Exclusions\n\n"
            "## Metadata\n"
            "- Total Files: 0\n"
            "- Total Tags: 0\n"
            "- Last Updated: 2025-01-15\n"
        )
    
    def _extract_type(self, file_path: str) -> str:
        """Extract file extension as type."""
        return Path(file_path).suffix.lstrip('.').lower() or 'unknown'
    
    def _load_data(self) -> Tuple[Dict[str, Dict], List, Dict]:
        """Load and parse tags.md into dicts."""
        content = self.tags_file.read_text()
        files = {}
        for match in re.finditer(r'### (.*?)\n- Type: (.*?)\n((?:- .*?\n)*)', content):
            file_path = match.group(1)
            file_type = match.group(2)
            tags_str = match.group(3)
            tags = [line[2:].strip() for line in tags_str.split('\n') if line.startswith('- ') and not line.startswith('- Type: ')]
            files[file_path] = {'tags': tags, 'type': file_type}
        return files, [], {}
    
    def _save_data(self, files: Dict[str, Dict], exclusions: List, metadata: Dict) -> None:
        """Save data back to tags.md."""
        content = "# Tagging System Data\n\n## Files and Tags\n\n"
        for file_path, data in sorted(files.items()):
            content += f"### {file_path}\n"
            content += f"- Type: {data['type']}\n"
            for tag in sorted(data['tags']):
                content += f"- {tag}\n"
            content += "\n"
        
        content += "## Tag Exclusions\n\n## Metadata\n"
        for key, value in metadata.items():
            content += f"- {key}: {value}\n"
        
        self.tags_file.write_text(content)
    
    def add_tags(self, file_path: str, tags: List[Tuple[str, str]]) -> None:
        """Add tags to a file."""
        files, exclusions, metadata = self._load_data()
        file_type = self._extract_type(file_path)
        
        if file_path not in files:
            files[file_path] = {'tags': [], 'type': file_type}
        else:
            files[file_path]['type'] = file_type  # Update type if changed
        
        separator = self.config.get('separator', '/')
        for tag_key, tag_value in tags:
            full_tag = f"{tag_key}{separator}{tag_value}" if tag_value else tag_key
            if full_tag not in files[file_path]['tags']:
                files[file_path]['tags'].append(full_tag)
        
        # Update metadata
        metadata['Total Files'] = str(len(files))
        metadata['Total Tags'] = str(sum(len(data['tags']) for data in files.values()))
        from datetime import datetime
        metadata['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self._save_data(files, exclusions, metadata)
    
    def get_tags(self, file_path: str) -> List[str]:
        """Get tags for a file."""
        files, _, _ = self._load_data()
        return files.get(file_path, {}).get('tags', [])
    
    def search(self, query: str, type_filter: str = None, fuzzy: bool = False) -> Dict[str, List[str]]:
        """Search files by tags."""
        files, _, _ = self._load_data()
        results = {}
        
        if fuzzy:
            from fuzzywuzzy import fuzz
            threshold = 70
            for file_path, data in files.items():
                if type_filter and data['type'] != type_filter:
                    continue
                matching_tags = [tag for tag in data['tags'] if any(fuzz.partial_ratio(query, part) >= threshold for part in tag.split('/'))]
                if matching_tags:
                    results[file_path] = data['tags']
        else:
            query = query.replace('*', '.*')
            for file_path, data in files.items():
                if type_filter and data['type'] != type_filter:
                    continue
                try:
                    if any(re.search(query, tag) for tag in data['tags']):
                        results[file_path] = data['tags']
                except re.error:
                    pass
        
        return results
    
    def remove_tags(self, file_path: str, tags: List[Tuple[str, str]]) -> None:
        """Remove tags from a file."""
        files, exclusions, metadata = self._load_data()
        if file_path in files:
            separator = self.config.get('separator', '/')
            for tag_key, tag_value in tags:
                full_tag = f"{tag_key}{separator}{tag_value}" if tag_value else tag_key
                if full_tag in files[file_path]['tags']:
                    files[file_path]['tags'].remove(full_tag)
            metadata['Total Tags'] = str(sum(len(data['tags']) for data in files.values()))
            from datetime import datetime
            metadata['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._save_data(files, exclusions, metadata)
    
    def rename_tag(self, old_tag: str, new_tag: str) -> None:
        """Rename a tag across all files."""
        files, exclusions, metadata = self._load_data()
        for file_data in files.values():
            if old_tag in file_data['tags']:
                file_data['tags'].remove(old_tag)
                file_data['tags'].append(new_tag)
        from datetime import datetime
        metadata['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._save_data(files, exclusions, metadata)
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        files, _, _ = self._load_data()
        all_tags = set()
        for data in files.values():
            all_tags.update(data['tags'])
        return list(all_tags)
    
    def get_all_data(self) -> Dict[str, List[str]]:
        """Get all file-tag data."""
        files, _, _ = self._load_data()
        return {k: v['tags'] for k, v in files.items()}
    
    def batch_apply(self, folder_path: str, tag: Tuple[str, str], type_filter: str = None) -> int:
        """Apply tag to files in folder."""
        count = 0
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_type = self._extract_type(file_path)
                if not type_filter or file_type == type_filter:
                    self.add_tags(file_path, [tag])
                    count += 1
        return count