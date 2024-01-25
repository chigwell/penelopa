import unittest
from unittest.mock import patch, mock_open
from penelopa.configuration import ConfigManager
import os

class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.default_config_path = 'penelopa-config.yaml'

    def test_default_config(self):
        config_manager = ConfigManager()
        self.assertIsNotNone(config_manager.config)
        self.assertIn('project', config_manager.config)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="project: TestProject\nmodel: gpt-4")
    def test_load_existing_valid_config(self, mock_file, mock_exists):
        mock_exists.return_value = True
        config_manager = ConfigManager(self.default_config_path)
        curr_dir = os.getcwd()
        self.assertEqual(config_manager.project, curr_dir)
        self.assertEqual(config_manager.model, "gpt-4-1106-preview")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="invalid_yaml")
    @patch('logging.error')
    def test_load_invalid_config(self, mock_logging, mock_file, mock_exists):
        mock_exists.return_value = True
        config_manager = ConfigManager(self.default_config_path)
        self.assertDictEqual(config_manager.config, ConfigManager.DEFAULT_CONFIG)

    @patch('tempfile.NamedTemporaryFile')
    @patch('shutil.move')
    @patch('yaml.safe_dump')
    def test_save_config(self, mock_safe_dump, mock_move, mock_tempfile):
        config_manager = ConfigManager()
        config_manager.save_config()
        mock_safe_dump.assert_called_once()
        mock_move.assert_called_once()
        default_config_path = os.getcwd() + '/' + self.default_config_path
        if os.path.exists(default_config_path):
            os.remove(default_config_path)

    def test_update_config_valid(self):
        config_manager = ConfigManager()
        config_manager.update_config(project='NewProject')
        self.assertEqual(config_manager.project, 'NewProject')
        default_config_path = os.getcwd() + '/' + self.default_config_path
        if os.path.exists(default_config_path):
            os.remove(default_config_path)

    def test_update_config_invalid(self):
        config_manager = ConfigManager()
        original_config = config_manager.config.copy()
        config_manager.update_config(invalid_key='invalid_value')
        self.assertDictEqual(config_manager.config, original_config)
        default_config_path = os.getcwd() + '/' + self.default_config_path
        if os.path.exists(default_config_path):
            os.remove(default_config_path)

if __name__ == '__main__':
    unittest.main()
