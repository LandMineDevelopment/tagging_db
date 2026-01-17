import unittest
from unittest.mock import MagicMock, patch
import tempfile
from pathlib import Path
from src.storage.markdown import MarkdownStorage
from src.storage.database import DatabaseStorage
from src.config import ConfigManager

class TestStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_mock = MagicMock()
        self.config_mock.get_storage_path.return_value = self.temp_dir
        self.config_mock.get.return_value = '/'

    def test_markdown_storage_init_creates_file(self):
        storage = MarkdownStorage(self.config_mock)
        expected_file = Path(self.temp_dir) / "tags.md"
        self.assertEqual(storage.tags_file, expected_file)
        self.assertTrue(expected_file.exists())

    def test_database_storage_init_creates_db(self):
        storage = DatabaseStorage(self.config_mock)
        expected_db = Path(self.temp_dir) / "tags.db"
        # Check if engine is created with correct path
        self.assertIn(str(expected_db), str(storage.engine.url))

    def test_markdown_add_tags_absolute_path(self):
        storage = MarkdownStorage(self.config_mock)
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("content")
        storage.add_tags(str(test_file), [("key", "value")])
        tags = storage.get_tags(str(test_file))
        self.assertIn("key/value", tags)

    def test_markdown_add_tags_relative_path(self):
        storage = MarkdownStorage(self.config_mock)
        test_file = Path("relative_test.txt")
        test_file.write_text("content")
        abs_path = str(test_file.resolve())
        storage.add_tags(str(test_file), [("key", "value")])
        tags = storage.get_tags(str(test_file))
        self.assertIn("key/value", tags)
        # Check stored with absolute
        data = storage.get_all_data()
        self.assertIn(abs_path, data)

    def test_database_add_tags_absolute_path(self):
        storage = DatabaseStorage(self.config_mock)
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("content")
        storage.add_tags(str(test_file), [("key", "value")])
        tags = storage.get_tags(str(test_file))
        self.assertIn("key/value", tags)

    def test_database_add_tags_relative_path(self):
        storage = DatabaseStorage(self.config_mock)
        test_file = Path("relative_test_db.txt")
        test_file.write_text("content")
        abs_path = str(test_file.resolve())
        storage.add_tags(str(test_file), [("key", "value")])
        tags = storage.get_tags(str(test_file))
        self.assertIn("key/value", tags)
        # Check stored with absolute
        data = storage.get_all_data()
        self.assertIn(abs_path, data)

if __name__ == '__main__':
    unittest.main()