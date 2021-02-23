import json
import logging
from typing import Union
from ws_sdk import constants
from datetime import datetime
from secrets import compare_digest
from memoization import cached

import requests

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

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
        """SDK for WhiteSource
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

    @cached(ttl=constants.CACHE_TIME)
    def __set_token_in_body__(self, kv_dict,
                              token: str) -> str:
        if token is None:
            token_type = self.token_type
        else:
            token_type = self.get_scope_type_by_token(token)
            kv_dict[self.TOKEN_TYPES[token_type]] = token
            logging.debug(f"Token: {token} is a {token_type}")

        return token_type

    @cached(ttl=constants.CACHE_TIME)
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

    @cached(ttl=constants.CACHE_TIME)
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
            logging.error(f"Error while retrieving API:{request_type} Error: {resp.text}")
        else:
            logging.debug("API %s call on %s succeeded" % (body['requestType'], body[token[0]]))

        try:
            ret = json.loads(resp.text)
        except json.JSONDecodeError:
            logging.debug("Not a JSON object")
            ret = resp.content

        return ret

    @cached(ttl=constants.CACHE_TIME)
    def __generic_get__(self,
                        get_type: str,
                        token_type: str,
                        kv_dict: dict = None) -> [list, dict, bytes]:
        """
        This function completer the API type and calls.
        :param get_type:
        :param token_type:
        :param kv_dict:
        :return: can be list, dict, none or bytes (pdf, xlsx...)
        :rtype: list or dict or bytes
        """
        return self.__call_api__(f"get{token_type.capitalize()}{get_type}", kv_dict)

    # Covers O/P/P + byType + report
    def get_alerts(self,
                   token: str = None,
                   alert_type: str = None,
                   from_date: datetime = None,
                   to_date: datetime = None,
                   project_tag: bool = False,
                   tag: dict = {},
                   ignored: bool = False,
                   resolved: bool = False,
                   report: bool = False) -> Union[list, bytes]:
        """
        :param token: The token that the request will be created on
        :param alert_type: Allows filtering alerts by a single type from ALERT_TYPES
        :param from_date: Allows filtering of alerts by start date. Works together with to_date
        :param to_date: Allows filtering of alerts by end date. Works together with from_date
        :param project_tag: should filter by project tags
        :param tag: dict of Key:Value of the tag. Allowed only 1 pair
        :param ignored: Should output include ignored reports
        :param resolved: Should output include resolved reports
        :param report: Create xlsx report type
        :return: list with alerts or xlsx if report is True
        :rtype: list or bytes
        """
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)

        if alert_type in self.ALERT_TYPES:
            kv_dict["alertType"] = alert_type
        elif alert_type:
            logging.error(f"Alert: {alert_type} does not exist")
            return

        if isinstance(from_date, datetime):
            kv_dict["fromDate"] = from_date.strftime(DATE_FORMAT)
        if isinstance(to_date, datetime):
            kv_dict["toDate"] = to_date.strftime(DATE_FORMAT)

        ret = None
        if resolved and report:
            logging.debug("Running Resolved Alerts Report")
            ret = self.__call_api__(f"get{token_type.capitalize()}ResolvedAlertsReport", kv_dict)
        elif ignored and report:
            logging.debug("Running ignored Alerts Report")
            ret = self.__call_api__(f"get{token_type.capitalize()}IgnoredAlertsReport", kv_dict)
        elif resolved:
            logging.error("Resolved Alerts is only in xlsx format")
        elif ignored:
            logging.debug("Running ignored Alerts")
            ret = self.__call_api__(f"get{token_type.capitalize()}IgnoredAlerts", kv_dict)
        elif report:
            logging.debug("Running Alerts Report")
            kv_dict["format"] = "xlsx"
            ret = self.__call_api__(f"get{token_type.capitalize()}AlertsReport", kv_dict)
        elif project_tag:
            if token_type != constants.ORGANIZATION:
                logging.error("Getting project alerts tag is only supported with organization token")
            elif len(tag) == 1:
                logging.debug("Running Alerts by project tag")
                ret = self.__call_api__("getAlertsByProjectTag", kv_dict)
            else:
                logging.error("Alerts tag is not set correctly")
        elif kv_dict.get('alertType') is not None:
            logging.debug("Running Alerts By Type")
            ret = self.__call_api__(f"get{token_type.capitalize()}AlertsByType", kv_dict)
        else:
            logging.debug("Running Alerts")
            ret = self.__call_api__(f"get{token_type.capitalize()}Alerts", kv_dict)

        return ret.get('alerts') if isinstance(ret, dict) else ret

    def get_inventory(self,
                      token: str = None,
                      include_in_house_data: bool = True,
                      report: bool = False) -> [list, bytes]:
        """
        :param token: The token that the request will be created on
        :param include_in_house_data:
        :param report:
        :return: list or xlsx if report is True
        :rtype: list or bytes
        """
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        ret = None
        if report:
            logging.debug("Running Inventory Report")
            kv_dict["format"] = "xlsx"
            ret = self.__call_api__(f"get{token_type.capitalize()}InventoryReport", kv_dict)
        elif token_type == 'project':
            logging.debug(f"Running {token_type} Inventory")
            kv_dict["includeInHouseData"] = include_in_house_data
            ret = self.__call_api__(f"get{token_type.capitalize()}Inventory", kv_dict)
        else:
            logging.error(f"get inventory is unsupported on {token_type}")

        return ret['libraries'] if isinstance(ret, dict) else ret

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

    def get_scope_from_name(self, scope_name):
        scopes = self.get_all_scopes()
        for scope in scopes:
            if scope_name == scope['name']:
                return scope
        logging.error(f"{scope_name} was not found")

    def get_token_from_name(self,
                            name: str) -> str:
        scope = self.get_scope_from_name(name)

        return None if scope is None else scope['token']

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

    def get_vulnerability(self,
                          status: str = None,  # "Active", "Ignored", "Resolved"
                          container: bool = False,
                          cluster: bool = False,
                          report: bool = False,
                          token: str = None) -> Union[list, bytes]:
        """
        :param status: str Alert status: "Active", "Ignored", "Resolved"
        :param container:
        :param cluster:
        :param report:
        :param token: The token that the request will be created on
        :return: list or xlsx if report is True
        :rtype: list or bytes
        """
        kv_dict = {}
        if not report:
            kv_dict["format"] = "json"
        token_type = self.__set_token_in_body__(kv_dict, token)
        if status is not None:
            kv_dict['status'] = status
        # ret = None
        if container:       # TODO: Check if this is a bug. Does not work my org neither with orgToken nor productToken
            ret = self.__call_api__(f"get{token_type.capitalize()}ContainerVulnerabilityReport", kv_dict)
            # if token_type == 'product':
            #     logging.debug("Running container Vulnerability Report")
            #     ret = self.__call_api__(f"get{token_type.capitalize()}ContainerVulnerabilityReport", kv_dict)
            # else:
            #     logging.error(f"get organization container vulnerability report is unsupported on {token_type}")
        elif cluster:       # TODO: Check if this is a bug. Does not work my org neither with orgToken nor productToken
            ret = self.__call_api__(f"getClusterVulnerabilityReport", kv_dict)
        else:
            logging.debug(f"Running {token_type.capitalize()} Vulnerability Report")
            ret = self.__call_api__(f"get{token_type.capitalize()}VulnerabilityReport", kv_dict)

        return ret['vulnerabilities'] if isinstance(ret, dict) else ret

    def get_vulnerabilities_per_lib(self,
                                    token: str = None) -> list:
        # Internal method
        def get_highest_severity(comp_severity, severity):
            sev_dict = {"high": 3, "medium": 2, "low": 1, "none": 0}

            return comp_severity if sev_dict[comp_severity] > sev_dict[severity] else severity

        vuls = self.get_vulnerability(token=token)
        logging.debug(f"Found {len(vuls)} Vulnerabilities")
        libs_vul = {}
        for vul in vuls:
            lib = vul['library']
            key_uuid = lib['keyUuid']
            if not libs_vul.get(key_uuid):
                lib_dict = {}
                for key in lib.keys():
                    lib_dict[key] = lib[key]
                lib_dict['vulnerabilities'] = set()
                lib_dict['severity'] = "none"
                libs_vul[key_uuid] = lib_dict
            libs_vul[key_uuid]['vulnerabilities'].add(vul['name'])
            curr_severity = vul['severity']
            libs_vul[key_uuid]['severity'] = get_highest_severity(curr_severity, libs_vul[key_uuid]['severity'])
        logging.debug(f"Found {len(libs_vul)} libraries with vulnerabilities")

        return list(libs_vul.values())

    def get_change_log(self,
                       start_date: datetime = None) -> list:
        report_name = 'Change Log Report'
        if start_date is None:
            kv_dict = None
        else:
            kv_dict = {'startDateTime': start_date.strftime("%Y-%m-%d %H:%M:%S")}
        logging.debug(f"Running {report_name}")

        return self.__call_api__("getChangesReport", kv_dict)['changes']

    def get_licenses(self,
                     token: str = None,
                     exclude_project_occurrences: bool = False) -> list:
        report_name = 'licenses Report'
        kv_dict = {'excludeProjectOccurrences': exclude_project_occurrences}
        token_type = self.__set_token_in_body__(kv_dict, token)
        logging.debug(f"Running {token_type} {report_name}")

        return self.__generic_get__(get_type='Licenses', token_type=token_type, kv_dict=kv_dict)['libraries']

    def get_source_files(self,
                         token: str = None,
                         report: bool = False) -> Union[list, bytes]:
        report_name = 'Source File Inventory Report'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if report:
            kv_dict["format"] = "xlsx"
            logging.debug(f"Running {token_type} {report_name}")
        else:
            kv_dict["format"] = "json"
            logging.debug(f"Running {token_type} Inventory")
        ret = self.__generic_get__(get_type='SourceFileInventoryReport', token_type=token_type, kv_dict=kv_dict)

        return ret['sourceFiles'] if isinstance(ret, dict) else ret

    def get_in_house_libraries(self,
                               report: bool = False,
                               token: str = None) -> Union[list, bytes]:
        """
        :param report: get output as xlsx if True
        :param token: The token that the request will be created on
        :return: list or bytes(xlsx)
        :rtype: list or bytes
        """
        report_name = 'In-House Libraries'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if report:
            logging.debug(f"Running {token_type} {report_name} Report")
            ret = self.__generic_get__(get_type='InHouseReport', token_type=token_type, kv_dict=kv_dict)
        else:
            logging.debug(f"Running {token_type} {report_name}")
            ret = self.__generic_get__(get_type='InHouseLibraries', token_type=token_type, kv_dict=kv_dict)['libraries']

        return ret['sourceFiles'] if isinstance(ret, dict) else ret

    def get_assignments(self,
                        token: str = None):
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if token_type == constants.PROJECT:
            logging.error("get assignment is unsupported on project")
        else:
            logging.debug(f"Running {token_type} Assignment")
            return self.__generic_get__(get_type='Assignments', token_type=token_type, kv_dict=kv_dict)

    def get_risk(self,
                 token: str = None) -> bytes:
        """API for WhiteSource
        :token: Token of scope
        :token_type: Scope Type (organization, product, project)
        :return bytes (pdf)
        :rtype: bytes
        """
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if token_type == constants.PROJECT:
            logging.error("get risk is unsupported on project")
        else:
            logging.debug(f"Running {token_type} RiskReport")
            return self.__generic_get__(get_type='RiskReport', token_type=token_type, kv_dict=kv_dict)

    def get_library_location(self,
                             token: str = None) -> bytes:
        report_name = 'Library Location Report'
        """
        :param token: The token that the request will be created on
        :return: bytes (xlsx)
        :rtype bytes
        """
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if token_type == constants.PROJECT:
            logging.error(f"{report_name} is unsupported on project level")
        else:
            logging.debug(f"Running {report_name} on {token_type}")
            return self.__generic_get__(get_type='LibraryLocationReport', token_type=token_type, kv_dict=kv_dict)

    def get_license_compatibility(self,
                                  token: str = None) -> bytes:
        report_name = 'License Compatibility Report'
        """
        :param token: The token that the request will be created on
        :return: bytes (xlsx)
        :rtype bytes
        """
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if token_type == constants.ORGANIZATION:
            logging.error(f"{report_name} is unsupported on organization level")
        else:
            logging.debug(f"Running {report_name} on {token_type}")
            return self.__generic_get__(get_type='LicenseCompatibilityReport', token_type=token_type, kv_dict=kv_dict)

    def get_due_diligence(self,
                          token: str = None,
                          report: bool = False) -> Union[list, bytes]:
        report_name = 'Due Diligence Report'
        """
        :param token: The token that the request will be created on str
        :param token: The token that the request will be created on bool - Should 
        :return: list or bytes (xlsx)
        :rtype list or bytes
        """
        kv_dict = {}
        if not report:
            kv_dict["format"] = "json"
        token_type = self.__set_token_in_body__(kv_dict, token)
        logging.debug(f"Running {report_name} on {token_type}")
        ret = self.__generic_get__(get_type='DueDiligenceReport', token_type=token_type, kv_dict=kv_dict)

        return ret['licenses'] if isinstance(ret, dict) else ret

    def get_attributes(self,
                       token: str = None) -> bytes:
        """
        :param token: The token that the request will be created on
        :return: bytes (xlsx)
        :rtype bytes
        """
        report_name = 'Attributes Report'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if token_type == constants.PROJECT:
            logging.error(f"{report_name} is unsupported on project")
        else:
            logging.debug(f"Running {token_type} {report_name}")
            return self.__generic_get__(get_type='AttributesReport', token_type=token_type, kv_dict=kv_dict)

    def get_effective_licenses(self,
                               token: str = None) -> bytes:
        """
        :param token: The token that the request will be created on
        :return: bytes (xlsx)
        :rtype bytes
        """
        report_name = 'Effective Licenses Report'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        if token_type == constants.PROJECT:
            logging.error(f"{report_name} is unsupported on project")
        else:
            logging.debug(f"Running {token_type} {report_name}")
            return self.__generic_get__(get_type='EffectiveLicensesReport', token_type=token_type, kv_dict=kv_dict)

    def get_bugs(self,
                 token: str = None) -> bytes:
        """
        :param token: The token that the request will be created on
        :return: bytes (xlsx)
        :rtype bytes
        """
        report_name = 'Bugs Report'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        logging.debug(f"Running {token_type} {report_name}")

        return self.__generic_get__(get_type='BugsReport', token_type=token_type, kv_dict=kv_dict)

    def get_request_history(self,
                            plugin: bool = False,
                            token: str = None) -> bytes:
        """
        :param plugin: bool
        :param token: The token that the request will be created on str
        :return: bytes (xlsx)
        :rtype bytes
        """
        report_name = 'Request History Report'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        ret = None
        if plugin and token_type == constants.ORGANIZATION:
            ret = self.__generic_get__(get_type='PluginRequestHistoryReport', token_type=token_type, kv_dict=kv_dict)
        elif plugin:
            logging.error(f"Plugin {report_name} unsupported for {token_type}")
        else:
            logging.debug(f"Running {token_type} {report_name}")
            ret = self.__generic_get__(get_type='RequestHistoryReport', token_type=token_type, kv_dict=kv_dict)

        return ret

    def get_license_histogram(self,
                              token: str = None) -> list:
        """
        :param token: The token that the request will be created on
        :return: list
        :rtype list
        """
        report_name = 'License Histogram'
        kv_dict = {}
        token_type = self.__set_token_in_body__(kv_dict, token)
        logging.debug(f"Running {report_name}")

        return self.__generic_get__(get_type='LicenseHistogram', token_type=token_type, kv_dict=kv_dict)['licenseHistogram']
