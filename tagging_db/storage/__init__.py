from abc import ABC, abstractmethod
from tagging_db.storage.markdown import MarkdownStorage
from tagging_db.storage.database import DatabaseStorage

class StorageInterface(ABC):
    @abstractmethod
    def add_tags(self, file_path, tags):
        pass
    
    @abstractmethod
    def get_tags(self, file_path):
        pass
    
    @abstractmethod
    def search(self, query, type_filter=None):
        pass
    
    @abstractmethod
    def batch_apply(self, folder_path, tag, type_filter=None):
        pass

class StorageFactory:
    @staticmethod
    def create(config):
        if config.get('storage') == 'db':
            return DatabaseStorage(config)
        return MarkdownStorage(config)