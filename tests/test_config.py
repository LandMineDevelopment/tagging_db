import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path
from src.config import ConfigManager

class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.config_manager = ConfigManager()

    @patch('src.config.Path.home')
    def test_set_storage_path_valid_absolute(self, mock_home):
        mock_home.return_value = Path('/home/user')
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch.object(self.config_manager, 'save') as mock_save:
            self.config_manager.set_storage_path('/absolute/path/to/storage')
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            self.assertEqual(self.config_manager.data['storage_path'], '/absolute/path/to/storage')
            mock_save.assert_called_once()

    @patch('src.config.Path.home')
    def test_set_storage_path_relative_raises_error(self, mock_home):
        mock_home.return_value = Path('/home/user')
        with self.assertRaises(ValueError) as context:
            self.config_manager.set_storage_path('relative/path')
        self.assertIn("must be absolute", str(context.exception))

    @patch('src.config.Path.home')
    @patch('src.config.yaml.safe_load')
    def test_get_storage_path_set(self, mock_load, mock_home):
        mock_home.return_value = Path('/home/user')
        mock_load.return_value = {'storage_path': '/some/path'}
        self.config_manager.current_config_file = '/fake/config'
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='storage_path: /some/path\n')):
            path = self.config_manager.get_storage_path()
            self.assertEqual(path, '/some/path')

    @patch('src.config.Path.home')
    @patch('src.config.yaml.safe_load')
    def test_get_storage_path_unset_raises_error(self, mock_load, mock_home):
        mock_home.return_value = Path('/home/user')
        mock_load.return_value = {}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='')):
            with self.assertRaises(ValueError) as context:
                self.config_manager.get_storage_path()
            self.assertIn("not set", str(context.exception))

if __name__ == '__main__':
    unittest.main()