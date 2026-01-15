import pytest
from tagging_db.config import ConfigManager

class TestConfigManager:
    def test_load_defaults(self):
        config = ConfigManager()
        assert config.get('storage') == 'md'
        assert config.get('separator') == '/'
    
    def test_load_from_file(self, tmp_path):
        config_file = tmp_path / '.testconfig'
        config_file.write_text('storage: db\nseparator: .\n')
        config = ConfigManager()
        config.load(str(config_file))
        assert config.get('storage') == 'db'
        assert config.get('separator') == '.'