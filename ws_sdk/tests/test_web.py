import unittest
from mock import patch, MagicMock, Mock
from web import WS

c = WS(api_url="wss_api_url", user_key="user_key1", token="org_token1", token_type="organization")


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

    @patch('web.WS.get_vitals')
    def test_get_all_tokens(self, mock_get_vitals):
        with patch('web.WS') as ws_class:
            ws_class.return_value.token_type = "organization"
            mock_get_vitals.return_value = list()
            res = c.get_all_tokens()
            self.assertIsInstance(res, list)

    def test_get_alerts_by_type(self):
        with patch('web.WS') as ws_class:
            pass


if __name__ == '__main__':
    unittest.main()
