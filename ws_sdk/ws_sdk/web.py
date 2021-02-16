import json
import logging
from datetime import datetime
from secrets import compare_digest

import requests

HEADERS = {'content-type': 'application/json'}


class WS:
    TOKEN_TYPES = {"organization": "orgToken",
                   "product": "productToken",
                   "project": "projectToken"
                   }
    ALERT_TYPES = ['SECURITY_VULNERABILITY', 'NEW_MAJOR_VERSION', 'NEW_MINOR_VERSION', 'MULTIPLE_LIBRARY_VERSIONS', 'REJECTED_BY_POLICY_RESOURCE']

    def __init__(self,
                 api_url: str,
                 user_key: str,
                 token: str,
                 token_type: str = 'organization',
                 timeout: int = 30,
                 resp_format: str = "json"
                 ):
        """API for WhiteSource
        :api_url: URL for the API to access (e.g. saas.whitesourcesoftware.com)
        :user_key: User Key to use
        :token: Token of scope
        :token_type: Scope Type (organization, product, project)
        """
        self.api_url = api_url
        self.user_key = user_key
        self.token = token
        self.token_type = token_type
        self.timeout = timeout
        self.resp_format = resp_format

        if token_type != 'organization':
            logging.error("Currently only supporting organization")
            return

    def __create_body__(self,
                        api_call: str,
                        kv_dict: dict = None) -> dict:
        ret_dict = {
            "requestType": api_call,
            "userKey": self.user_key,
            self.TOKEN_TYPES[self.token_type]: self.token
        }
        if isinstance(kv_dict, dict):
            for ent in kv_dict:
                ret_dict[ent] = kv_dict[ent]

        return ret_dict

    def __call_api__(self,
                     request_type: str,
                     kv_dict: dict = None) -> dict:
        body = self.__create_body__(request_type, kv_dict)
        # adapter = requests.adapters.HTTPAdapter(max_retries=3)
        token = [s for s in body.keys() if 'Token' in s]
        # s = requests.Session()
        # s.mount(self.api_url, adapter)
        try:
            # resp = s.post(self.api_url, data=json.dumps(body), headers=HEADERS, timeout=self.timeout)
            resp = requests.post(self.api_url, data=json.dumps(body), headers=HEADERS, timeout=self.timeout)
        except Exception as e:
            logging.error(f"Received Error on {body[token[0]]} {e}")
            raise

        if resp.status_code > 299:
            logging.error("API %s call on %s failed" % (body['requestType'], body[token[0]]))
        elif "errorCode" in resp.text:
            logging.error(f"Error while retrieving API: {resp.text}")
        else:
            logging.debug("API %s call on %s succeeded" % (body['requestType'], body[token[0]]))

        try:
            ret = json.loads(resp.text)
        except json.JSONDecodeError:
            logging.debug("Not a JSON object")
            ret = resp.content

        return ret

    # Covers O/P/P + byType + report
    def get_alerts(self,
                   token: str = None,
                   alert_type: str = None,
                   from_date: datetime = None,
                   to_date: datetime = None,
                   report: bool = False) -> [list, bytes]:
        kv_dict = {}
        if token is None:                                       # Running call on WS token
            token_type = self.token_type
        else:                                                   # Running call on specified token
            token_type = self.get_scope_type_by_token(token)
            kv_dict[self.TOKEN_TYPES[token_type]] = token
            logging.debug(f"Token: {token} is a {token_type}")

        if alert_type in self.ALERT_TYPES:
            kv_dict["alertType"] = alert_type
        elif alert_type:
            logging.error(f"Alert: {alert_type} does not exist")
            return

        if isinstance(from_date, datetime):
            kv_dict["fromDate"] = from_date
        if isinstance(to_date, datetime):
            kv_dict["toDate"] = to_date

        if report:
            logging.debug("Running Alerts Report")
            kv_dict["format"] = "xlsx"

            return self.__call_api__(f"get{token_type.capitalize()}AlertsReport", kv_dict)
        elif kv_dict.get('alertType') is not None:
            logging.debug("Running Alerts By Type")

            return self.__call_api__(f"get{token_type.capitalize()}AlertsByType", kv_dict)['alerts']
        else:
            logging.debug("Running Alerts")

            return self.__call_api__(f"get{token_type.capitalize()}Alerts", kv_dict)['alerts']

    def get_inventory(self,
                      token: str = None,
                      include_in_house_data: bool = True,
                      report: bool = False) -> [list, bytes]:
        kv_dict = {}
        if token is None:                                       # Running call on WS token
            token_type = self.token_type
        else:                                                   # Running call on specified token
            token_type = self.get_scope_type_by_token(token)
            kv_dict[self.TOKEN_TYPES[token_type]] = token
            logging.debug(f"Token: {token} is of {token_type}")

        if report:
            logging.debug("Running Inventory Report")
            kv_dict["format"] = "xlsx"

            return self.__call_api__(f"get{token_type.capitalize()}InventoryReport", kv_dict)
        elif token_type == 'project':
            logging.debug(f"Running {token_type} Inventory")
            kv_dict["includeInHouseData"] = include_in_house_data
            return self.__call_api__(f"get{token_type.capitalize()}Inventory", kv_dict)['libraries']
        else:
            logging.error(f"get inventory is unsupported on {token_type}")

    def get_scope_type_by_token(self,
                                token: str) -> str:
        tok = self.get_scope_by_token(token)
        if tok is not None:
            return tok['type']

    def get_scope_name_by_token(self,
                                token: str) -> str:
        tok = self.get_scope_by_token(token)
        if tok is not None:
            return tok['name']

    def get_scope_by_token(self,
                           token: str) -> dict:
        tokens = self.get_all_scopes()
        for tok in tokens:
            if compare_digest(tok['token'], token):
                logging.debug(f"Found token: {token}")
                return tok
        logging.debug(f"Token {token} was not found")

    def get_all_scopes(self) -> list:
        all_tokens = list()
        if self.token_type == "organization":
            projects = self.get_vitals("project")
            for project in projects:
                project['type'] = "project"
            products = self.get_vitals("product")
            for product in products:
                product['type'] = "product"
            all_tokens = products + projects

        return all_tokens

    def get_vitals(self,
                   of_type: str) -> list:
        return self.__call_api__(f"get{self.token_type.capitalize()}{of_type.capitalize()}Vitals")[f"{of_type}Vitals"]

    def get_organization_details(self) -> dict:
        return self.__call_api__("getOrganizationDetails") if (self.token_type == 'organization') \
            else logging.error("get organization details only allowed on organization")

    def get_organization_name(self) -> str:
        return self.get_organization_details()['orgName']

    def get_token_from_name(self,
                            project_name: str) -> str:
        logging.debug(f"Searching for project: {project_name} token")
        all_products = WS.get_all_products()
        all_projects = []
        for product in all_products:
            project_response = WS.get_all_projects()
            all_projects += project_response.get('projects')

        for project in all_projects:
            if project['projectName'].lower() == project_name.lower():
                logging.debug(f"Found token: {project['projectToken']}")
                return project['projectToken']

        logging.error(f"Project name: {project_name} was not found")

    def get_scope_by_name(self, scope_name):
        scopes = self.get_all_scopes()
        for scope in scopes:
            if scope_name == scope['name']:
                return scope
        logging.error(f"{scope_name} was not found")

    def get_scope_token_by_name(self, scope_name):
        return self.get_scope_by_name(scope_name)['token']

    def get_all_products(self) -> list:
        return self.__call_api__("getAllProducts")['products'] if self.token_type == 'organization' \
            else logging.error("get_all_products only allowed on organization")

    def get_all_projects(self,
                         token=None) -> list:
        ret = None
        if self.token_type == 'project':
            logging.error("get_all_projects only allowed on organizations or products")
        elif self.token_type == 'product':
            ret = self.__call_api__("getAllProjects")['projects']
        elif token is not None:
            ret = self.__call_api__("getAllProjects", kv_dict={self.TOKEN_TYPES['product']: token})['projects']
        else:
            ret = list(filter(lambda tok: (tok['type'] == 'project'), self.get_all_scopes()))

        return ret

    # def get_product_vulnerabilities(self):
    #     return json.loads(self, self.api_url, WS.call_api(
    #         create_body("getProductVulnerabilityReport", self.user_key, self.product_token, "productToken")))[
    #         'vulnerabilities']
    #
    # def get_project_vulnerabilities(self):
    #     return json.loads(self, self.api_url, WS.call_api(
    #         create_body("getProjectVulnerabilityReport", self.user_key, self.project_token, "projectToken")))[
    #         'vulnerabilities']
    #
    # def get_highest_severity(self, curr_severity, severity):
    #     sev_dict = {"high": 3,
    #                 "medium": 2,
    #                 "low": 1,
    #                 "none": 0
    #                 }
    #     return curr_severity if sev_dict[curr_severity] > sev_dict[severity] else severity
    #
    # def get_scope_name(self, scope_token, report_scope):
    #     if report_scope == "organization":
    #         scope_name = self.get_organization_name(self, self.api_url, self.user_key, self.org_token)
    #     elif report_scope == "product":
    #         scope_name = self.get_product_name(self, self.api_url, self.user_key, self.org_token, scope_token)
    #     elif report_scope == "project":
    #         scope_name = self.get_product_name(self, self.api_url, self.user_key, self.org_token, scope_token)
    #
    #     return scope_name
    #
    # # Get vulnerabilities per library
    # def get_vulnerabilities_per_lib(self, report_scope):
    #     report_scopes = {
    #         "organization": self.get_organization_vulnerabilities,
    #         "product": self.get_product_vulnerabilities,
    #         "project": self.get_project_vulnerabilities
    #     }
    #     report_method = report_scopes.get(report_scope)
    #     vuls = report_method(self, self.api_url, self.user_key, self.token)
    #
    #     libs_vul = {}
    #     for vul in vuls:
    #         lib = vul['library']
    #         key_uuid = lib['keyUuid']
    #         if not libs_vul.get(key_uuid):
    #             lib_dict = {}
    #             for key in lib.keys():
    #                 lib_dict[key] = lib[key]
    #             lib_dict['vulnerabilities'] = set()
    #             lib_dict['severity'] = "none"
    #             libs_vul[key_uuid] = lib_dict
    #         libs_vul[key_uuid]['vulnerabilities'].add(vul['name'])
    #         curr_severity = vul['severity']
    #         libs_vul[key_uuid]['severity'] = self.get_highest_severity(curr_severity, libs_vul[key_uuid]['severity'])
    #
    #     return libs_vul
    #
    # # Provides flatten list of all projects (name, token, dates) under product
    # def get_product_project_vitals(self):
    #     return json.loads(
    #         self.call_api(self, self.api_url, create_body("getProductProjectVitals", self.user_key, self.product_token, "productToken")))[
    #         "projectVitals"]
    #
    # def get_organization_name(self):
    #     return self.get_organization_details(self, self.api_url, self.user_key, self.org_token).get('orgName')
    #
    # def get_product_name(self, token):
    #     products = self.get_organization_product_vitals(self, self.api_url, self.user_key, self.org_token)
    #     for product in products:
    #         if product['token'] == token: return product['name']
    #
    # def get_project_name(self, token):
    #     projects = self.get_organization_project_vitals(self, self.api_url, self.user_key, self.org_token)
    #     for project in projects:
    #         if project['token'] == token: return project['name']
    #
    # def get_product_vitals(self):  # TODO DELETE?
    #     return json.loads(self, self.api_url, self.call_api(create_body("getProductVitals", self.user_key, self.product_token, "productToken")))[
    #         "productVitals"]
    #
    # def get_project_vitals(self):
    #     return json.loads(self, self.api_url, self.call_api(create_body("getProjectVitals", self.user_key, self.project_token, "projectToken")))[
    #         "projectVitals"]
    #

    # Deprecated
    # def get_organization_product_vitals(self):
    #     return json.loads(self.call_api("getOrganizationProductVitals"))["productVitals"]
    #
    # def get_organization_project_vitals(self):
    #     return json.loads(self.call_api("getOrganizationProjectVitals"))["projectVitals"]
