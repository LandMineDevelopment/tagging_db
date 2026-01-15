import os
import yaml
from pathlib import Path

class MarkdownStorage:
    def __init__(self, config):
        self.config = config
        self.tags_file = Path(config.get('tags_file', 'tags.md'))
        self.separator = config.get('separator', '/')
        if not self.tags_file.exists():
            self.tags_file.write_text("# Tagging System Data\n\n## Files and Tags\n\n## Tag Exclusions\n\n## Metadata\n- Total Files: 0\n- Total Tags: 0\n- Last Updated: 2025-01-15\n")
    
    def _extract_type(self, file_path):
        """Extract file extension as type."""
        return Path(file_path).suffix.lstrip('.').lower() or 'unknown'
    
    def _load_data(self):
        """Load and parse tags.md into a dict."""
        content = self.tags_file.read_text()
        files = {}
        import re
        for match in re.finditer(r'### (.*?)\n- Type: (.*?)\n((?:- .*?\n)*)', content):
            file_path = match.group(1)
            file_type = match.group(2)
            tags_str = match.group(3)
            tags = [line[2:].strip() for line in tags_str.split('\n') if line.startswith('- ') and not line.startswith('- Type: ')]
            files[file_path] = {'tags': tags, 'type': file_type}
        return files, {}, {}
    
    def _save_data(self, files, exclusions, metadata):
        """Save data back to tags.md."""
        content = "# Tagging System Data\n\n## Files and Tags\n\n"
        for file_path, data in files.items():
            content += f"### {file_path}\n"
            content += f"- Type: {data['type']}\n"
            for tag in data['tags']:
                content += f"- {tag}\n"
            content += "\n"
        
        content += "## Tag Exclusions\n"
        for exc in exclusions:
            content += f"- {exc[0]} : {exc[1]}\n"
        content += "\n## Metadata\n"
        for key, value in metadata.items():
            content += f"- {key}: {value}\n"
        
        self.tags_file.write_text(content)
    
    def add_tags(self, file_path, tags):
        """Add tags to a file."""
        files, exclusions, metadata = self._load_data()
        file_type = self._extract_type(file_path)
        
        if file_path not in files:
            files[file_path] = {'tags': [], 'type': file_type}
        else:
            files[file_path]['type'] = file_type  # Update type if changed
        
        for tag_key, tag_value in tags:
            full_tag = f"{tag_key}{self.separator}{tag_value}" if tag_value else tag_key
            if full_tag not in files[file_path]['tags']:
                files[file_path]['tags'].append(full_tag)
        
        # Update metadata
        metadata['Total Files'] = str(len(files))
        metadata['Total Tags'] = str(sum(len(data['tags']) for data in files.values()))
        metadata['Last Updated'] = '2025-01-15'  # Use datetime
        
        self._save_data(files, exclusions, metadata)
    
    def get_tags(self, file_path):
        """Get tags for a file."""
        files, _, _ = self._load_data()
        return files.get(file_path, {}).get('tags', [])
    
    def search(self, query, type_filter=None):
        """Search files by tags."""
        import re
        files, _, _ = self._load_data()
        results = {}
        
        # Convert * wildcards to .* for regex
        query = query.replace('*', '.*')
        
        for file_path, data in files.items():
            if type_filter and data['type'] != type_filter:
                continue
            try:
                if any(re.search(query, tag) for tag in data['tags']):
                    results[file_path] = data['tags']
            except re.error:
                # If invalid regex, skip
                pass
        
        return results
    
    def batch_apply(self, folder_path, tag, type_filter=None):
        """Apply tag to all files in folder matching type."""
        count = 0
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_type = self._extract_type(file_path)
                if not type_filter or file_type == type_filter:
                    self.add_tags(file_path, [tag])
                    count += 1
        return count