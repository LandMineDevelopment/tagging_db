import pytest
from unittest.mock import patch
from tagging_db.engine import TagEngine
from tagging_db.config import ConfigManager

class TestTagEngine:
    @pytest.fixture
    def config(self):
        return ConfigManager()
    
@pytest.fixture
def engine(config):
    return TagEngine(config)
    
    def test_add_tags_valid_file(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('work', 'project')])
        tags = engine.get_tags(str(test_file))
        assert 'work/project' in tags
    
    def test_add_tags_invalid_file(self, engine):
        with pytest.raises(ValueError, match="File does not exist"):
            engine.add_tags('nonexistent.txt', [('work', 'project')])
    
    def test_batch_apply_invalid_folder(self, engine):
        with pytest.raises(ValueError, match="Folder does not exist"):
            engine.batch_apply('nonexistent', ('work', 'project'))