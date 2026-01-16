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
def storage(config, tmp_path):
    config.data['tags_file'] = str(tmp_path / 'tags.md')
    return MarkdownStorage(config)

@pytest.fixture
def db_storage(config, tmp_path):
    config.data['storage'] = 'db'
    config.data['db_path'] = str(tmp_path / 'test.db')
    from tagging_db.storage.database import DatabaseStorage
    return DatabaseStorage(config)

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
    
    def test_search_with_wildcard(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        storage.add_tags('other.md', [('personal', '')])
        results = storage.search('work*')
        assert 'test.txt' in results
        assert 'other.md' not in results
        results_star = storage.search('*work')
        assert 'test.txt' in results_star  # 'work/project' contains 'work'
    
    def test_search_invalid_regex(self, storage):
        storage.add_tags('test.txt', [('work', '')])
        # Invalid regex should not crash
        results = storage.search('[invalid')
        assert isinstance(results, dict)  # Should return empty or valid
    
    def test_search_fuzzy(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        results = storage.search('work', fuzzy=True)  # Exact match
        assert 'test.txt' in results

    def test_remove_tags(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        storage.remove_tags('test.txt', [('work', '')])
        tags = storage.get_tags('test.txt')
        assert 'work' not in tags
    
    def test_rename_tag(self, storage):
        storage.add_tags('test.txt', [('old', '')])
        storage.rename_tag('old', 'new')
        tags = storage.get_tags('test.txt')
        assert 'new' in tags
        assert 'old' not in tags
    
    def test_get_all_tags(self, storage):
        storage.add_tags('test.txt', [('work', 'project')])
        storage.add_tags('other.md', [('personal', '')])
        all_tags = storage.get_all_tags()
        assert 'work/project' in all_tags
        assert 'personal' in all_tags

class TestDatabaseStorage:
    def test_add_tags_new_file(self, db_storage):
        db_storage.add_tags('test.txt', [('work', 'project')])
        tags = db_storage.get_tags('test.txt')
        assert 'work/project' in tags
        assert len(tags) == 1
    
    def test_add_tags_existing_file(self, db_storage):
        db_storage.add_tags('test.txt', [('work', 'project')])
        db_storage.add_tags('test.txt', [('personal', '')])
        tags = db_storage.get_tags('test.txt')
        assert 'work/project' in tags
        assert 'personal' in tags
    
    def test_get_tags_nonexistent(self, db_storage):
        tags = db_storage.get_tags('nonexistent.txt')
        assert tags == []
    
    def test_search(self, db_storage):
        db_storage.add_tags('test.txt', [('work', 'project')])
        db_storage.add_tags('other.md', [('personal', '')])
        results = db_storage.search('work')
        assert 'test.txt' in results
        assert results['test.txt'] == ['work/project']
    
    def test_search_with_type_filter(self, db_storage):
        db_storage.add_tags('test.txt', [('work', 'project')])
        db_storage.add_tags('other.md', [('work', 'project')])
        results = db_storage.search('work', 'txt')
        assert 'test.txt' in results
        assert 'other.md' not in results
    
    def test_search_with_wildcard(self, db_storage):
        db_storage.add_tags('test.txt', [('work', 'project')])
        db_storage.add_tags('other.md', [('personal', '')])
        results = db_storage.search('work*')
        assert 'test.txt' in results
        assert 'other.md' not in results
        results_star = db_storage.search('*work')
        assert 'test.txt' in results_star  # 'work/project' contains 'work'
    
    def test_search_invalid_regex(self, db_storage):
        db_storage.add_tags('test.txt', [('work', '')])
        # Invalid regex should not crash
        results = db_storage.search('[invalid')
        assert isinstance(results, dict)  # Should return empty or valid
    
    def test_search_fuzzy(self, db_storage):
        db_storage.add_tags('test.txt', [('work', 'project')])
        results = db_storage.search('work', fuzzy=True)  # Exact match
        assert 'test.txt' in results
    
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