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