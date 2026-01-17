import unittest
from unittest.mock import MagicMock, patch
import tempfile
from pathlib import Path
from src.engine import TagEngine
from src.config import ConfigManager

class TestTagEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_mock = MagicMock(spec=ConfigManager)
        self.config_mock.get_storage_path.return_value = self.temp_dir
        self.config_mock.get.return_value = '/'

    def test_engine_init_with_storage_path(self):
        """Test engine initializes and calls get_storage_path."""
        with patch('src.engine.StorageFactory.create'):
            engine = TagEngine(self.config_mock)
        self.config_mock.get_storage_path.assert_called_once()
        self.assertEqual(engine.storage_path, self.temp_dir)
        self.assertEqual(engine.history_file, Path(self.temp_dir) / 'tag_history.json')

    def test_engine_init_storage_path_unset_raises(self):
        """Test engine init raises if storage path not set."""
        self.config_mock.get_storage_path.side_effect = ValueError("Storage path is not set")
        with patch('src.engine.StorageFactory.create'):
            with self.assertRaises(ValueError) as context:
                TagEngine(self.config_mock)
        self.assertIn("not set", str(context.exception))

    def test_add_tags_resolves_path(self):
        """Test add_tags resolves file path to absolute."""
        storage_mock = MagicMock()
        with patch('src.engine.StorageFactory.create', return_value=storage_mock):
            engine = TagEngine(self.config_mock)
        test_file = Path("test.txt")
        test_file.write_text("content")
        abs_path = str(test_file.resolve())
        engine.add_tags(str(test_file), [("key", "value")])
        storage_mock.add_tags.assert_called_with(abs_path, [("key", "value")])

    def test_remove_tags_resolves_path(self):
        """Test remove_tags resolves file path."""
        storage_mock = MagicMock()
        with patch('src.engine.StorageFactory.create', return_value=storage_mock):
            engine = TagEngine(self.config_mock)
        test_file = Path("test_remove.txt")
        test_file.write_text("content")
        abs_path = str(test_file.resolve())
        engine.remove_tags(str(test_file), [("key", "value")])
        storage_mock.remove_tags.assert_called_with(abs_path, [("key", "value")])

    def test_get_tags_resolves_path(self):
        """Test get_tags resolves file path."""
        storage_mock = MagicMock()
        with patch('src.engine.StorageFactory.create', return_value=storage_mock):
            engine = TagEngine(self.config_mock)
        test_file = Path("test_get.txt")
        test_file.write_text("content")
        abs_path = str(test_file.resolve())
        engine.get_tags(str(test_file))
        storage_mock.get_tags.assert_called_with(abs_path)

    def test_batch_apply_resolves_folder_path(self):
        """Test batch_apply resolves folder path."""
        storage_mock = MagicMock()
        with patch('src.engine.StorageFactory.create', return_value=storage_mock):
            engine = TagEngine(self.config_mock)
        folder = Path(self.temp_dir) / "folder"
        folder.mkdir()
        abs_folder = str(folder.resolve())
        engine.batch_apply(str(folder), ("key", "value"))
        storage_mock.batch_apply.assert_called_with(abs_folder, ("key", "value"), None)

if __name__ == '__main__':
    unittest.main()