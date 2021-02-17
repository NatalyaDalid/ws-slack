import unittest
from datetime import datetime
from unittest import TestCase

from mock import patch

import ws_sdk.constants as constants
from ws_sdk.web import WS


class TestWS(TestCase):
    def setUp(self):
        self.ws = WS(api_url="WS_API_URL", user_key="USER_KEY", token="ORG_TOKEN", token_type=constants.ORGANIZATION)

    @patch('ws_sdk.web.WS.get_scope_type_by_token')
    def test___set_token_in_body__(self, mock_get_scope_type_by_token):
        mock_get_scope_type_by_token.return_value = constants.PRODUCT
        kv_dict = {}
        res = self.ws.__set_token_in_body__(kv_dict=kv_dict, token="TOKEN")

        self.assertIsInstance(res, str) and self.assertIn({'productToken': 'TOKEN'}, kv_dict)

    def test___create_body__(self):
        res = self.ws.__create_body__("api_call")

        self.assertIsInstance(res, dict)

    def test___create_body___with_dict(self):
        res = self.ws.__create_body__("api_call", {"key": "Value"})

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.requests.post')
    def test___call_api__(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '{"key": "val"}'
        res = self.ws.__call_api__("api_call")

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.__call_api__')
    def test___generic_get__(self, mock_call_api):
        mock_call_api.return_value = []
        res = self.ws.__generic_get__(token_type=self.ws.token_type, get_type='suffix', kv_dict={})

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.get_vitals')
    def test_get_all_scopes(self, mock_get_vitals):
        with patch('ws_sdk.web.WS') as ws_class:
            ws_class.return_value.token_type = constants.ORGANIZATION
            mock_get_vitals.return_value = list()
            res = self.ws.get_all_scopes()

            self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_report(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = bytes()
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_alerts(report=True)

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_report_on_product(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = bytes()
        mock_set_token_in_body.return_value = constants.PRODUCT
        res = self.ws.get_alerts(report=True, token="PROD_TOKEN")

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_by_type(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = {'alerts': dict()}
        mock_set_token_in_body.return_value = self.ws.token_type
        from_date = datetime.now()
        to_date = datetime.now()
        res = self.ws.get_alerts(alert_type='SECURITY_VULNERABILITY', from_date=from_date, to_date=to_date)

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    def test_get_alerts_by_false_type(self, mock_set_token_in_body):
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_alerts(alert_type='FALSE')

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_all(self, mock_call_api, mock_set_token_in_body):
        mock_set_token_in_body.return_value = self.ws.token_type
        mock_call_api.return_value = {'alerts': list()}
        res = self.ws.get_alerts()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_ignored(self, mock_call_api, mock_set_token_in_body):
        mock_set_token_in_body.return_value = self.ws.token_type
        mock_call_api.return_value = {'alerts': list()}
        res = self.ws.get_alerts(ignored=True)

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_alerts_by_project_tag(self, mock_call_api, mock_set_token_in_body):
        mock_set_token_in_body.return_value = self.ws.token_type
        mock_call_api.return_value = {'alerts': list()}
        res = self.ws.get_alerts(project_tag=True, tag={"key": "value"})

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    def test_get_alerts_by_project_tag_product_token(self, mock_set_token_in_body):
        mock_set_token_in_body.return_value = constants.PRODUCT
        res = self.ws.get_alerts(project_tag=True, tag={"key": "value"}, token=constants.PRODUCT)

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    def test_get_alerts_by_project_no_tag(self, mock_set_token_in_body):
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_alerts(project_tag=True)

        self.assertIs(res, None)

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
    def test_get_all_projects_as_project(self, mock_call_api):
        mock_call_api.return_value = {'projects': dict()}
        self.ws.token_type = constants.PROJECT
        res = self.ws.get_all_projects()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_projects_as_product(self, mock_call_api):
        mock_call_api.return_value = {'projects': list()}
        self.ws.token_type = constants.PRODUCT
        res = self.ws.get_all_projects()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_all_projects_as_org_project_token(self, mock_call_api):
        mock_call_api.return_value = {'projects': list()}
        res = self.ws.get_all_projects(token="PROD_TOKEN")

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_organization_details(self, mock_call_api):
        mock_call_api.return_value = dict()
        res = self.ws.get_organization_details()

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.get_organization_details')
    def test_get_organization_name(self, mock_get_organization_details):
        mock_get_organization_details.return_value = {'orgName': "ORG_NAME"}
        res = self.ws.get_organization_name()

        self.assertIsInstance(res, str)

    def test_get_organization_details_not_org(self):
        self.ws.token_type = constants.PRODUCT
        res = self.ws.get_organization_details()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_inventory_report(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = bytes()
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_inventory(report=True)

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_inventory__product_report(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = bytes()
        mock_set_token_in_body.return_value = constants.PRODUCT
        res = self.ws.get_inventory(report=True, token="PRODUCT")

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_inventory_project(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = {'libraries': list()}
        mock_set_token_in_body.return_value = constants.PROJECT
        res = self.ws.get_inventory(token="PROJECT")

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    def test_get_inventory(self, mock_set_token_in_body):
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_inventory()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.get_all_scopes')
    def test_get_scope_from_name(self, mock_get_all_scopes):
        mock_get_all_scopes.return_value = [{'name': "NAME", 'token': "TOKEN"}]
        res = self.ws.get_scope_from_name("NAME")

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.get_all_scopes')
    def test_get_scope_from_name_not_found(self, mock_get_all_scopes):
        mock_get_all_scopes.return_value = list()
        res = self.ws.get_scope_from_name("NAME")

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.get_scope_from_name')
    def test_get_token_from_name(self, mock_get_scope_from_name):
        mock_get_scope_from_name.return_value = {'name': "NAME", 'token': "TOKEN"}
        res = self.ws.get_token_from_name('NAME')

        self.assertIsInstance(res, str)

    @patch('ws_sdk.web.WS.get_scope_from_name')
    def test_get_token_from_name_not_found(self, mock_get_scope_from_name):
        mock_get_scope_from_name.return_value = None
        res = self.ws.get_token_from_name('NAME_NOT_FOUND')

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_vulnerability_report(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = {'vulnerabilities': list()}
        mock_set_token_in_body.return_value = self.ws.token_type

        res = self.ws.get_vulnerability_report()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_vulnerability_report_xlsx_of_product(self, mock_call_api, mock_set_token_in_body):
        mock_call_api.return_value = bytes()
        mock_set_token_in_body.return_value = constants.PRODUCT
        res = self.ws.get_vulnerability_report(token="PRODUCT", report=True)

        self.assertIsInstance(res, bytes)

    @patch('ws_sdk.web.WS.get_vulnerability_report')
    def test_get_vulnerabilities_per_lib(self, mock_get_vulnerability_report):
        mock_get_vulnerability_report.return_value = list()
        res = self.ws.get_vulnerabilities_per_lib()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__call_api__')
    def test_get_change_log_report(self, mock_call_api):
        mock_call_api.return_value = {'changes': list()}
        res = self.ws.get_change_log_report()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__generic_get__')
    def test_get_assignments(self, mock_generic_get, mock_set_token_in_body):
        mock_generic_get.return_value = dict()
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_assignments()

        self.assertIsInstance(res, dict)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    def test_get_assignments_project(self, mock_set_token_in_body):
        mock_set_token_in_body.return_value = constants.PROJECT
        res = self.ws.get_assignments()

        self.assertIs(res, None)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__generic_get__')
    def test_get_licenses(self, mock_generic_get, mock_set_token_in_body):
        mock_generic_get.return_value = {'libraries': list()}
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_licenses()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__generic_get__')
    def test_get_in_house_libraries(self, mock_generic_get, mock_set_token_in_body):
        mock_generic_get.return_value = {'libraries': list()}
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_in_house_libraries()

        self.assertIsInstance(res, list)

    @patch('ws_sdk.web.WS.__set_token_in_body__')
    @patch('ws_sdk.web.WS.__generic_get__')
    def test_get_licenses_histogram(self, mock_generic_get, mock_set_token_in_body):
        mock_generic_get.return_value = {'licenseHistogram': dict()}
        mock_set_token_in_body.return_value = self.ws.token_type
        res = self.ws.get_license_histogram()

        self.assertIsInstance(res, dict)


if __name__ == '__main__':
    unittest.main()
