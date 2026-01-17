from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class StorageInterface(ABC):
    @abstractmethod
    def add_tags(self, file_path, tags):
        pass
    
    @abstractmethod
    def remove_tags(self, file_path, tags):
        pass
    
    @abstractmethod
    def get_tags(self, file_path):
        pass
    
    @abstractmethod
    def search(self, query, type_filter: Optional[str] = None, fuzzy: bool = False):
        pass
    
    @abstractmethod
    def batch_apply(self, folder_path, tag, type_filter: Optional[str] = None):
        pass
    
    @abstractmethod
    def rename_tag(self, old_tag, new_tag):
        pass
    
    @abstractmethod
    def get_all_tags(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_all_data(self) -> Dict[str, List[str]]:
        pass