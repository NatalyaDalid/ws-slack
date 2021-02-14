import unittest
from datetime import datetime

from mock import patch, MagicMock, Mock, PropertyMock
from web import WS


class TestWS(unittest.TestCase):
    c = WS(api_url="wss_api_url", user_key="user_key1", token="org_token1", token_type="organization")      # TODO NEED TO REMOVE

    def test___create_body__(self):
        res = self.c.__create_body__("api_call")

        self.assertIsInstance(res, dict)

    def test___create_body___with_dict(self):
        res = self.c.__create_body__("api_call", {"key": "Value"})

        self.assertIsInstance(res, dict)

    @patch('web.requests')                            # Injecting mock for requests module. Object name is mock_request
    def test___call_api__(self, mock_requests):
        with patch('web.requests.post') as patched_post:  # Mocking post method so return value will include status_code attribute
            patched_post.return_value.status_code = 200
            patched_post.return_value.text = '{"key": "val"}'
            res = self.c.__call_api__("api_call")

            self.assertIsInstance(res, dict)

    @patch('web.WS.get_vitals')
    def test_get_all_tokens(self, mock_get_vitals):
        with patch('web.WS') as ws_class:
            ws_class.return_value.token_type = "organization"
            mock_get_vitals.return_value = list()
            res = self.c.get_all_tokens()

            self.assertIsInstance(res, list)

    @patch('web.WS.__call_api__')
    def test_get_alerts_report(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = dict()
            res = self.c.get_alerts(report=True)

            self.assertIsInstance(res, dict)

    @patch('web.WS.__call_api__')
    def test_get_alerts_by_type(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'alerts': dict()}
            from_date = datetime.now()
            to_date = datetime.now()
            res = self.c.get_alerts(alert_type='SECURITY_VULNERABILITY', from_date=from_date, to_date=to_date)

            self.assertIsInstance(res, dict)

    @patch('web.WS.__call_api__')
    def test_get_alerts_by_false_type(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'alerts': dict()}
            from_date = datetime.now()
            to_date = datetime.now()
            res = self.c.get_alerts(alert_type='FALSE', from_date=from_date, to_date=to_date)

            self.assertIs(res, None)

    @patch('web.WS.__call_api__')
    def test_get_alerts_all(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'alerts': dict()}
            res = self.c.get_alerts()

            self.assertIsInstance(res, dict)

    @patch('web.WS.__call_api__')
    def test_get_all_products(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'products': dict()}
            res = self.c.get_all_products()

            self.assertIsInstance(res, dict)

    @patch('web.WS.__call_api__')
    def test_get_all_products_with_product_token(self, mock_call_api):
        with patch('web.WS', new_callable=PropertyMock) as ws_class:
            self.c.token_type = 'products'
            mock_call_api.return_value = {'products': dict()}
            res = self.c.get_all_products()

            self.assertIs(res, None)

    @patch('web.WS.__call_api__')
    def test_get_all_projects(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'projects': dict()}
            res = self.c.get_all_projects()

            self.assertIsInstance(res, list)

    @patch('web.WS.__call_api__')
    def test_get_all_projects_project_token(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'projects': dict()}
            self.c.token_type = 'project'
            res = self.c.get_all_projects()

            self.assertIs(res, None)

    @patch('web.WS.__call_api__')
    def test_get_all_projects_project_token(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'projects': list()}
            self.c.token_type = 'product'
            res = self.c.get_all_projects()

            self.assertIsInstance(res, list)

    @patch('web.WS.__call_api__')
    def test_get_all_projects_project_token(self, mock_call_api):
        with patch('web.WS') as ws_class:
            mock_call_api.return_value = {'projects': list()}
            res = self.c.get_all_projects(token="PROD_TOKEN")

            self.assertIsInstance(res, list)


if __name__ == '__main__':
    unittest.main()
