import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from pathlib import Path
import tempfile
from src.tag import cli
from src.config import ConfigManager

class TestCLI(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    @patch('src.tag.app_config')
    @patch('src.tag.engine')
    def test_set_storage_valid_absolute_path(self, mock_engine, mock_config):
        mock_config.get_storage_path.side_effect = ValueError("not set")
        mock_config.set_storage_path = MagicMock()
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result = self.runner.invoke(cli, ['set_storage', '/absolute/path'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Storage location set to /absolute/path", result.output)
            mock_config.set_storage_path.assert_called_with('/absolute/path')

    @patch('src.tag.app_config')
    @patch('src.tag.engine')
    def test_set_storage_relative_path_error(self, mock_engine, mock_config):
        result = self.runner.invoke(cli, ['set_storage', 'relative/path'])
        self.assertEqual(result.exit_code, 0)  # Click doesn't exit on print
        self.assertIn("must be absolute", result.output)

    @patch('src.tag.app_config')
    @patch('src.tag.engine')
    def test_set_storage_same_path(self, mock_engine, mock_config):
        mock_config.get_storage_path.return_value = '/same/path'
        result = self.runner.invoke(cli, ['set_storage', '/same/path'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("already set to /same/path", result.output)

    @patch('src.tag.app_config')
    @patch('src.tag.engine')
    def test_set_storage_relocation(self, mock_engine, mock_config):
        mock_config.get_storage_path.return_value = '/old/path'
        mock_config.set_storage_path = MagicMock()
        mock_engine.relocate_storage = MagicMock()
        with patch('pathlib.Path.mkdir'):
            result = self.runner.invoke(cli, ['set_storage', '/new/path'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Relocated existing storage files to /new/path", result.output)
            mock_engine.relocate_storage.assert_called_with('/new/path')
            mock_config.set_storage_path.assert_called_with('/new/path')

if __name__ == '__main__':
    unittest.main()