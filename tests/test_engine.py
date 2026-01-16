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
    
    def test_remove_tags_valid(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('work', 'project')])
        engine.remove_tags(str(test_file), [('work', '')])
        tags = engine.get_tags(str(test_file))
        assert 'work' not in tags
    
    def test_rename_tag(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('old', '')])
        engine.rename_tag('old', 'new')
        tags = engine.get_tags(str(test_file))
        assert 'new' in tags
        assert 'old' not in tags
    
    def test_exclusions(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.config.data['exclusions'] = [['public', 'confidential']]
        engine.add_tags(str(test_file), [('public', '')])
        with pytest.raises(ValueError, match="conflicts"):
            engine.add_tags(str(test_file), [('confidential', '')])
    
    def test_get_stats(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('work', 'project'), ('personal', '')])
        stats = engine.get_stats()
        assert stats['total_tags'] >= 2
        assert 'work/project' in [t for t, c in stats['top_tags']]
    
    def test_undo_add(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('undo', 'tag')])
        tags_before = engine.get_tags(str(test_file))
        assert 'undo/tag' in tags_before
        msg = engine.undo()
        assert 'Undid add' in msg
        tags_after = engine.get_tags(str(test_file))
        assert 'undo/tag' not in tags_after
    
    def test_undo_remove(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('remove', 'tag')])
        engine.remove_tags(str(test_file), [('remove', 'tag')])
        assert 'remove/tag' not in engine.get_tags(str(test_file))
        msg = engine.undo()
        assert 'Undid remove' in msg
        assert 'remove/tag' in engine.get_tags(str(test_file))
    
    def test_undo_rename(self, engine, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        engine.add_tags(str(test_file), [('old', '')])
        engine.rename_tag('old', 'new')
        assert 'new' in engine.get_tags(str(test_file))
        msg = engine.undo()
        assert 'Undid rename' in msg
        assert 'old' in engine.get_tags(str(test_file))
    
    def test_batch_apply_invalid_folder(self, engine):
        with pytest.raises(ValueError, match="Folder does not exist"):
            engine.batch_apply('nonexistent', ('work', 'project'))