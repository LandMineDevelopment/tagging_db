import os
import yaml

class ConfigManager:
    def __init__(self):
        self.data = {
            'storage': 'md',
            'separator': '/',
            'index_memory_mb': 50,
            'colors': {'tag': 'green', 'error': 'red'}
        }
    
    def load(self, path):
        if os.path.exists(path):
            with open(path) as f:
                self.data.update(yaml.safe_load(f))
    
    def get(self, key, default=None):
        return self.data.get(key, default)