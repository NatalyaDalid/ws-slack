import unittest
from datetime import datetime
from unittest import TestCase

from mock import patch, PropertyMock
from ws_sdk.web import WS


class TestWS(TestCase):
    def setUp(self):
        self.ws = WS(api_url="ws_api_url", user_key="user_key1", token="org_token1", token_type="organization")

    def test___create_body__(self):
        res = self.ws.__create_body__("api_call")

        self.assertIsInstance(res, dict)

    def test___create_body___with_dict(self):
        res = self.ws.__create_body__("api_call", {"key": "Value"})

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.requests.post')
    def test___call_api__(self, patched_post):
        patched_post.return_value.status_code = 200
        patched_post.return_value.text = '{"key": "val"}'
        res = self.ws.__call_api__("api_call")

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.get_vitals')
    def test_get_all_scopes(self, mock_get_vitals):
        with patch('ws_sdk.web.WS') as ws_class:
            ws_class.return_value.token_type = "organization"
            mock_get_vitals.return_value = list()
            res = self.ws.get_all_scopes()

            self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_report(self, mock_call_api):
        mock_call_api.return_value = dict()
        res = self.ws.get_alerts(report=True)

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.get_scope_type_by_token')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_report_on_product(self, mock_call_api, mock_get_scope_type_by_token):
        mock_call_api.return_value = dict()
        mock_get_scope_type_by_token.return_value = 'product'
        res = self.ws.get_alerts(report=True, token="PROD_TOKEN")

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_by_type(self, mock_call_api):
        mock_call_api.return_value = {'alerts': dict()}
        from_date = datetime.now()
        to_date = datetime.now()
        res = self.ws.get_alerts(alert_type='SECURITY_VULNERABILITY', from_date=from_date, to_date=to_date)

        self.assertIsInstance(res, dict)

    def test_get_alerts_by_false_type(self):
        res = self.ws.get_alerts(alert_type='FALSE')

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_all(self, mock_call_api):
        mock_call_api.return_value = {'alerts': dict()}
        res = self.ws.get_alerts()

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_products(self, mock_call_api):
        mock_call_api.return_value = {'products': dict()}
        res = self.ws.get_all_products()

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_products_with_product_token(self, mock_call_api):
        self.ws.token_type = 'products'
        mock_call_api.return_value = {'products': dict()}
        res = self.ws.get_all_products()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.get_all_scopes')
    def test_get_all_projects(self, mock_get_all_scopes):
        mock_get_all_scopes.return_value = list()
        res = self.ws.get_all_projects()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_projects_project_token(self, mock_call_api):
        mock_call_api.return_value = {'projects': dict()}
        self.ws.token_type = 'project'
        res = self.ws.get_all_projects()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_projects_project_token(self, mock_call_api):
        mock_call_api.return_value = {'projects': list()}
        self.ws.token_type = 'product'
        res = self.ws.get_all_projects()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_projects_project_token(self, mock_call_api):
        mock_call_api.return_value = {'projects': list()}
        res = self.ws.get_all_projects(token="PROD_TOKEN")

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_organization_details(self, mock_call_api):
        mock_call_api.return_value = dict()
        res = self.ws.get_organization_details()

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.get_organization_details')
    def test_get_organization_details(self, mock_get_organization_details):
        mock_get_organization_details.return_value = {'orgName': "ORG_NAME"}
        res = self.ws.get_organization_name()

        self.assertIsInstance(res, str)

    def test_get_organization_details_not_org(self):
        self.ws.token_type = 'product'
        res = self.ws.get_organization_details()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_inventory_report(self, mock_call_api):
        mock_call_api.return_value = bytes()
        res = self.ws.get_inventory(report=True)

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.get_scope_type_by_token')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_inventory__product_report(self, mock_call_api, mock_get_scope_type_by_token):
        mock_call_api.return_value = bytes()
        mock_get_scope_type_by_token.return_value = 'product'
        res = self.ws.get_inventory(report=True, token="PRODUCT")

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.get_scope_type_by_token')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_inventory_project(self, mock_call_api, mock_get_scope_type_by_token):
        mock_call_api.return_value = {'libraries': list()}
        mock_get_scope_type_by_token.return_value = 'project'
        res = self.ws.get_inventory(token="PROJECT")

        self.assertIsInstance(res, list)

    def test_get_inventory(self):
        res = self.ws.get_inventory()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.get_all_scopes')
    def test_get_scope_by_name(self, mock_get_all_scopes):
        mock_get_all_scopes.return_value = [{'name': "NAME", 'token': "TOKEN"}]
        res = self.ws.get_scope_by_name("NAME")

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.get_all_scopes')
    def test_get_scope_by_name_not_found(self, mock_get_all_scopes):
        mock_get_all_scopes.return_value = list()
        res = self.ws.get_scope_by_name("NAME")

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.get_scope_by_name')
    def test_get_scope_token_by_name(self, mock_get_scope_by_name):
        mock_get_scope_by_name.return_value = {'name': "NAME", 'token': "TOKEN"}
        res = self.ws.get_scope_token_by_name('NAME')

        self.assertIsInstance(res, str)


if __name__ == '__main__':
    unittest.main()
