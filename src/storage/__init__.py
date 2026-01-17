from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional
from .markdown import MarkdownStorage
# from .database import DatabaseStorage

class StorageInterface(ABC):
    @abstractmethod
    def add_tags(self, file_path: str, tags: List[Tuple[str, str]]) -> None:
        pass
    
    @abstractmethod
    def get_tags(self, file_path: str) -> List[str]:
        pass
    
    @abstractmethod
    def search(self, query: str, type_filter: Optional[str] = None, fuzzy: bool = False) -> Dict[str, List[str]]:
        pass
    
    @abstractmethod
    def batch_apply(self, folder_path: str, tag: Tuple[str, str], type_filter: Optional[str] = None) -> int:
        pass
    
    @abstractmethod
    def remove_tags(self, file_path: str, tags: List[Tuple[str, str]]) -> None:
        pass
    
    @abstractmethod
    def rename_tag(self, old_tag: str, new_tag: str) -> None:
        pass
    
    @abstractmethod
    def get_all_tags(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_all_data(self) -> Dict[str, List[str]]:
        pass

class StorageFactory:
    @staticmethod
    def create(config):
        if config.get('storage') == 'db':
            raise ValueError("Database storage not available")
        return MarkdownStorage(config)