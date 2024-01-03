import os
import yaml
import logging
import tempfile
import shutil

class ConfigManager:
    DEFAULT_CONFIG = {
        'project': os.getcwd(),
        'path': os.getcwd(),
        'model': 'gpt-4-1106-preview',
        'gitignore': True,
        'temperature': 0.1,
        'top_p': 1.0,
        'max_tokens': 1500,
        'task': '',
        'logging': False,
        'assistant_id': '',
        'listing': '',
        'updated_listing': '',
        'gpt_key': ''
    }

    def __init__(self, config_path='penelopa-config.yaml'):
        self.config_path = config_path
        self.config = self.load_or_create_config()
        self._set_attributes()

    def load_or_create_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    if self._validate_config(config):
                        return config
                    else:
                        logging.warning("Invalid configuration format. Using default configuration.")
            except (yaml.YAMLError, IOError) as e:
                logging.error(f"Error reading configuration file: {e}. Using default configuration.")
        return ConfigManager.DEFAULT_CONFIG.copy()

    def _validate_config(self, config):
        required_keys = ConfigManager.DEFAULT_CONFIG.keys()
        return all(key in config for key in required_keys)

    def _set_attributes(self):
        for key, value in self.config.items():
            setattr(self, key, value)

    def save_config(self):
        try:
            with tempfile.NamedTemporaryFile('w', delete=False) as tf:
                yaml.safe_dump(self.config, tf)
                temp_name = tf.name
            shutil.move(temp_name, self.config_path)
        except IOError as e:
            logging.error(f"Error saving configuration file: {e}")
        else:
            logging.info("Configuration saved successfully.")

    def update_config(self, **kwargs):
        self.config.update(kwargs)
        if not self._validate_config(self.config):
            logging.error("Invalid configuration update.")
            return
        self._set_attributes()
        self.save_config()
