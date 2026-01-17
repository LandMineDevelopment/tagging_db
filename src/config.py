"""
Configuration management for the tagging system.
Handles loading, saving, and accessing config options.
"""
import os
from pathlib import Path
from typing import Dict, Any
import yaml

class ConfigManager:
    """Manages application configuration with defaults and persistence."""

    def __init__(self):
        self.config_path = Path.home() / ".tagging" / "config"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_config_file = None  # Track the loaded config file
        self.data: Dict[str, Any] = {
            'storage': 'md',  # 'md' or 'db'
            'separator': '/',  # Tag separator
            'index_memory_mb': 50,  # Memory limit for indexing
            'colors': {'tag': 'green', 'error': 'red'},  # CLI colors
            'exclusions': []  # List of excluded tag pairs
        }
    
    def load(self, path: str) -> None:
        """Load config from YAML file, updating defaults."""
        self.current_config_file = path
        if os.path.exists(path):
            with open(path) as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    self.data.update(loaded)
    
    def save(self, path: str = None) -> None:
        """Save current config to YAML file."""
        save_path = path or self.current_config_file or str(self.config_path)
        with open(save_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        return self.data.get(key, default)

    def set_storage_path(self, new_path: str) -> None:
        """Set the storage path, validate it, create directory if needed, and save to config."""
        path_obj = Path(new_path)
        if not path_obj.is_absolute():
            raise ValueError("Storage path must be absolute")
        path_obj.mkdir(parents=True, exist_ok=True)
        self.data['storage_path'] = str(path_obj)
        self.save()

    def get_storage_path(self) -> str:
        """Get the storage path from config, load if necessary."""
        # Load from current config file if set
        if self.current_config_file:
            self.load(self.current_config_file)
        path = self.data.get('storage_path')
        if path is None:
            raise ValueError("Storage path is not set")
        return path