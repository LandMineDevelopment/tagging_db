import os
import yaml
"""
Core engine for tag operations, coordinating storage and config.
"""
import os
import json
import shutil
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from .storage import StorageFactory
from .config import ConfigManager

class TagEngine:
    """Handles tag operations with validation and exclusions."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.storage_path = config.get_storage_path()
        self.storage = StorageFactory.create(config)
        self.history_file = Path(self.storage_path) / 'tag_history.json'
        self.history: List[Dict[str, Any]] = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load operation history."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return []
    
    def _save_history(self) -> None:
        """Save operation history."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _log_operation(self, op_type: str, **kwargs) -> None:
        """Log an operation for undo."""
        self.history.append({'type': op_type, **kwargs})
        if len(self.history) > 10:  # Keep last 10
            self.history.pop(0)
        self._save_history()
    
    def undo(self) -> str:
        """Undo the last operation."""
        if not self.history:
            raise ValueError("No operations to undo")
        
        last_op = self.history.pop()
        self._save_history()
        
        op_type = last_op['type']
        if op_type == 'add_tags':
            self.storage.remove_tags(last_op['file_path'], last_op['tags'])
            return f"Undid add tags to {last_op['file_path']}"
        elif op_type == 'remove_tags':
            self.storage.add_tags(last_op['file_path'], last_op['tags'])
            return f"Undid remove tags from {last_op['file_path']}"
        elif op_type == 'rename_tag':
            self.storage.rename_tag(last_op['new_tag'], last_op['old_tag'])
            return f"Undid rename '{last_op['new_tag']}' back to '{last_op['old_tag']}'"
        else:
            raise ValueError(f"Cannot undo operation: {op_type}")
    
    def add_tags(self, file_path: str, tags: List[Tuple[str, str]]) -> None:
        """Add tags to a file, checking exclusions."""
        file_path = str(Path(file_path).resolve())
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        current_tags = set(self.get_tags(file_path))
        exclusions = self.config.get('exclusions', [])
        separator = self.config.get('separator', '/')
        
        for tag_key, tag_value in tags:
            full_tag = f"{tag_key}{separator}{tag_value}" if tag_value else tag_key
            for exc in exclusions:
                if full_tag in exc and any(t in exc for t in current_tags):
                    raise ValueError(f"Tag '{full_tag}' conflicts with existing tags per exclusion rule: {exc}")
        
        self.storage.add_tags(file_path, tags)
        self._log_operation('add_tags', file_path=file_path, tags=tags)
    
    def remove_tags(self, file_path: str, tags: List[Tuple[str, str]]) -> None:
        """Remove tags from a file."""
        file_path = str(Path(file_path).resolve())
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        self.storage.remove_tags(file_path, tags)
        self._log_operation('remove_tags', file_path=file_path, tags=tags)
    
    def get_tags(self, file_path: str) -> List[str]:
        """Get tags for a file."""
        file_path = str(Path(file_path).resolve())
        return self.storage.get_tags(file_path)
    
    def search(self, query: str, type_filter: Optional[str] = None, fuzzy: bool = False) -> Dict[str, List[str]]:
        """Search files by tags."""
        return self.storage.search(query, type_filter, fuzzy)
    
    def batch_apply(self, folder_path: str, tag: Tuple[str, str], type_filter: Optional[str] = None) -> int:
        """Apply tag to files in folder."""
        folder_path = str(Path(folder_path).resolve())
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Folder does not exist: {folder_path}")
        return self.storage.batch_apply(folder_path, tag, type_filter)
    
    def rename_tag(self, old_tag: str, new_tag: str) -> None:
        """Rename a tag across all files."""
        self.storage.rename_tag(old_tag, new_tag)
        self._log_operation('rename_tag', old_tag=old_tag, new_tag=new_tag)
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        return self.storage.get_all_tags()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tag statistics."""
        tags = self.get_all_tags()
        tag_counts = {}
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return {
            'total_tags': len(tags),
            'unique_tags': len(set(tags)),
            'top_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def relocate_storage(self, new_path: str) -> None:
        """Relocate storage files to new path, handling DB locks."""
        current_path = self.config.get_storage_path()
        current_path_obj = Path(current_path)
        new_path_obj = Path(new_path)
        
        if self.config.get('storage') == 'db':
            # Close DB connections to avoid locks
            if hasattr(self.storage, 'Session'):
                self.storage.Session.close_all()
            if hasattr(self.storage, 'engine'):
                self.storage.engine.dispose()
        
        # Move all files from current path to new path
        if current_path_obj.exists():
            for item in current_path_obj.iterdir():
                if item.is_file():
                    shutil.move(str(item), str(new_path_obj / item.name))
                elif item.is_dir():
                    shutil.move(str(item), str(new_path_obj / item.name))