import pytest
import tempfile
import os
from pathlib import Path
from tagging_db.storage.markdown import MarkdownStorage
from tagging_db.config import ConfigManager

@pytest.fixture
def config():
    return ConfigManager()

@pytest.fixture
def storage(config):
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False)
    temp_file.close()
    config.data['tags_file'] = temp_file.name
    return MarkdownStorage(config)

class TestMarkdownStorage:
    def test_add_tags_new_file(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        tags = storage.get_tags('test.txt')
        assert 'work/project' in tags
        assert len(tags) == 1
    
    def test_add_tags_existing_file(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        storage.add_tags('test.txt', [('personal', '')])
        tags = storage.get_tags('test.txt')
        assert 'work/project' in tags
        assert 'personal' in tags
    
    def test_get_tags_nonexistent(self, storage):
        tags = storage.get_tags('nonexistent.txt')
        assert tags == []
    
    def test_search(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        storage.add_tags('other.md', [('personal', '')])
        results = storage.search('work')
        assert 'test.txt' in results
        assert results['test.txt'] == ['work/project']
    
    def test_search_with_type_filter(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        storage.add_tags('other.md', [('work', 'project')])
        results = storage.search('work', 'txt')
        assert 'test.txt' in results
        assert 'other.md' not in results
    
    def test_batch_apply(self, storage, tmp_path):
        # Create test files
        file1_path = str(tmp_path / 'file1.txt')
        file2_path = str(tmp_path / 'file2.txt')
        file3_path = str(tmp_path / 'file3.md')
        (tmp_path / 'file1.txt').write_text('content')
        (tmp_path / 'file2.txt').write_text('content')
        (tmp_path / 'file3.md').write_text('content')
        
        count = storage.batch_apply(str(tmp_path), ('work', 'project'), 'txt')
        assert count == 2
        assert 'work/project' in storage.get_tags(file1_path)
        assert 'work/project' in storage.get_tags(file2_path)
        assert 'work/project' not in storage.get_tags(file3_path)