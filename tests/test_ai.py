import unittest
from unittest.mock import MagicMock, patch
from penelopa.ai import AIClient
from unittest.mock import PropertyMock


class TestAIClient(unittest.TestCase):

    def setUp(self):
        self.api_key = 'test_api_key'
        self.model = 'test_model'

    @patch('tiktoken.encoding_for_model')
    def test_count_tokens(self, mock_encoding):
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3]
        mock_encoding.return_value = mock_encoder

        self.ai_client = AIClient(api_key=self.api_key, model=self.model)
        text = "Hello world"
        token_count = self.ai_client.count_tokens(text)
        self.assertGreater(token_count, 0)

if __name__ == '__main__':
    unittest.main()
