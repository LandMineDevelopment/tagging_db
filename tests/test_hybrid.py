import pytest
from tagging_db.engine import TagEngine
from tagging_db.config import ConfigManager

class TestHybridStorage:
    def test_switch_to_db(self, tmp_path):
        config = ConfigManager()
        config.data['storage'] = 'md'
        config.data['tags_file'] = str(tmp_path / 'tags.md')
        config.data['db_path'] = str(tmp_path / 'tags.db')
        engine = TagEngine(config)
        
        # Add in MD
        engine.add_tags('test.txt', [('md', 'tag')])
        assert 'md/tag' in engine.get_tags('test.txt')
        
        # Switch to DB
        config.data['storage'] = 'db'
        engine = TagEngine(config)
        
        # DB should start empty (no migration yet)
        assert engine.get_tags('test.txt') == []
        
        # Add in DB
        engine.add_tags('test.txt', [('db', 'tag')])
        assert 'db/tag' in engine.get_tags('test.txt')
    
    def test_migration_md_to_db(self, tmp_path):
        config = ConfigManager()
        config.data['storage'] = 'md'
        config.data['tags_file'] = str(tmp_path / 'tags.md')
        config.data['db_path'] = str(tmp_path / 'tags.db')
        engine = TagEngine(config)
        
        # Create test files
        file1 = tmp_path / 'file1.txt'
        file2 = tmp_path / 'file2.txt'
        file1.write_text('content')
        file2.write_text('content')
        
        # Add multiple data in MD
        engine.add_tags(str(file1), [('work', 'project'), ('urgent', '')])
        engine.add_tags(str(file2), [('personal', '')])
        assert 'work/project' in engine.get_tags(str(file1))
        assert 'personal' in engine.get_tags(str(file2))
        
        # Migrate to DB
        from tagging_db.storage.database import DatabaseStorage
        new_storage = DatabaseStorage(config)
        all_data = engine.storage.get_all_data()
        for file_path, tags in all_data.items():
            new_storage.add_tags(file_path, [(tag, '') for tag in tags])
        
        # Switch engine to DB
        config.data['storage'] = 'db'
        engine = TagEngine(config)
        
        # Check all data migrated
        assert 'work/project' in engine.get_tags(str(file1))
        assert 'urgent' in engine.get_tags(str(file1))
        assert 'personal' in engine.get_tags(str(file2))
    
    def test_migration_db_to_md(self, tmp_path):
        config = ConfigManager()
        config.data['storage'] = 'db'
        config.data['tags_file'] = str(tmp_path / 'tags.md')
        config.data['db_path'] = str(tmp_path / 'tags.db')
        engine = TagEngine(config)
        
        # Create test file
        test_file = tmp_path / 'file1.txt'
        test_file.write_text('content')
        
        # Add data in DB
        engine.add_tags(str(test_file), [('db', 'tag')])
        assert 'db/tag' in engine.get_tags(str(test_file))
        
        # Migrate to MD
        from tagging_db.storage.markdown import MarkdownStorage
        new_storage = MarkdownStorage(config)
        all_data = engine.storage.get_all_data()
        for file_path, tags in all_data.items():
            new_storage.add_tags(file_path, [(tag, '') for tag in tags])
        
        # Switch engine to MD
        config.data['storage'] = 'md'
        engine = TagEngine(config)
        
        # Check data migrated
        assert 'db/tag' in engine.get_tags(str(test_file))