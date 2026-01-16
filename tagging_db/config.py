"""
Configuration management for the tagging system.
Handles loading, saving, and accessing config options.
"""
import os
from typing import Dict, Any
import yaml

class ConfigManager:
    """Manages application configuration with defaults and persistence."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {
            'storage': 'md',  # 'md' or 'db'
            'separator': '/',  # Tag separator
            'index_memory_mb': 50,  # Memory limit for indexing
            'colors': {'tag': 'green', 'error': 'red'},  # CLI colors
            'exclusions': []  # List of excluded tag pairs
        }
    
    def load(self, path: str) -> None:
        """Load config from YAML file, updating defaults."""
        if os.path.exists(path):
            with open(path) as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    self.data.update(loaded)
    
    def save(self, path: str) -> None:
        """Save current config to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        return self.data.get(key, default)
    
    def get(self, key, default=None):
        return self.data.get(key, default)