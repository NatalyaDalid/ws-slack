import unittest
from mock import patch
from web import WSS

c = WSS(api_url="wss_api_url", user_key="user_key1", token="org_token1", token_type="organization")


class TestWeb(unittest.TestCase):
    def test_create_body(self):
        res = c.__create_body__("api_call")
        self.assertIsInstance(res, dict)

    def test_create_body_with_dict(self):
        res = c.__create_body__("api_call", {"key": "Value"})
        self.assertIsInstance(res, dict)

    @patch('web.requests')                            # Injecting mock for requests module. Object name is mock_request
    def test_call_api(self, mock_requests):
        with patch('web.requests.post') as patched_post:  # Mocking post method so return value will include status_code attribute
            patched_post.return_value.status_code = 200
            patched_post.return_value.text = '{"key": "val"}'
            res = c.__call_api__("api_call")
            self.assertIsInstance(res, dict)


if __name__ == '__main__':
    unittest.main()
