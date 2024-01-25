import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from penelopa.penelopa import Penelopa

class TestPenelopa(unittest.TestCase):

    @patch('penelopa.penelopa.Penelopa.save_config')
    @patch('tiktoken.encoding_for_model')
    def test_init(self, mock_encoding, mock_save_config):
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3]
        mock_encoding.return_value = mock_encoder

        config = {'project': 'TestProject', 'gpt_key': 'dummy_key', 'model': 'gpt-3'}
        penelopa = Penelopa(config)
        self.assertEqual(penelopa.config['project'], 'TestProject')

if __name__ == '__main__':
    unittest.main()
