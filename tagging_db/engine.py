import os
import yaml
from tagging_db.storage import StorageFactory

class TagEngine:
    def __init__(self, config):
        self.config = config
        self.storage = StorageFactory.create(config)
    
    def add_tags(self, file_path, tags):
        if not os.path.exists(file_path):
            raise ValueError("File does not exist")
        self.storage.add_tags(file_path, tags)
    
    def get_tags(self, file_path):
        return self.storage.get_tags(file_path)
    
    def search(self, query, type_filter=None):
        return self.storage.search(query, type_filter)
    
    def batch_apply(self, folder_path, tag, type_filter=None):
        if not os.path.isdir(folder_path):
            raise ValueError("Folder does not exist")
        return self.storage.batch_apply(folder_path, tag, type_filter)