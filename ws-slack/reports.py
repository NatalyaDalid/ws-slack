import json
import logging
from abc import ABC
import slack_actions
from ws_sdk.web import WS
import slack_format


class Report(ABC):
    def __init__(self,
                 ws_conn_details: dict,
                 config: dict,
                 ws_connector: WS):
        self.ws_conn_details = ws_conn_details
        self.config = config
        self.ws_connector = ws_connector
        self.execute() if is_valid_config(self.ws_conn_details,
                                          self.mandatory_values,
                                          self.config['MandatoryWsConnProp'] + self.MANDATORY_PROPS) else KeyError

    def create_report_metadata(self) -> tuple:
        scope = self.ws_connector.get_scope_by_token(token=self.ws_conn_details['ws_scope_token'])
        channel = self.get_channel_name(scope_type=scope['type'], scope_token=self.ws_conn_details['ws_scope_token'])
        header_text = f"{scope['type']} {scope['name']} {self.report_name}"

        return scope, channel, header_text

    def get_channel_name(self, scope_type, scope_token) -> str:
        channel_name = f"{self.config['ChannelPrefix']}{scope_type}_{self.ws_connector.get_scope_name_by_token(token=scope_token)}"

        return slack_actions.fix_slack_channel_name(channel_name)


class Alerts(Report):
    MANDATORY_PROPS = ['ws_scope_token']
    report_name = "Library Vulnerability report"

    def execute(self):
        alerts = self.ws_connector.get_alerts(token=self.ws_conn_details['ws_scope_token'])
        scope, channel, header_text = self.create_report_metadata()

        block = []
        slack_actions.send_to_slack(channel=channel, block=json.dumps(block))
        logging.info(f"Successfully executed: {self.report_name}")


class LibVulnerabilities(Report):
    MANDATORY_PROPS = ['ws_scope_token']
    report_name = "Library Vulnerability report"

    def execute(self):
        libs = self.ws_connector.get_vulnerabilities_per_lib(token=self.ws_conn_details['ws_scope_token'])
        scope, channel, header_text = self.create_report_metadata()

        block = slack_format.create_lib_vul_block(header_text, libs)
        slack_actions.send_to_slack(channel=channel, block=json.dumps(block))
        logging.info(f"Successfully executed: {self.report_name}")


def is_valid_config(matched_dict, mandatory_keys):    # TODO: Add syntax validation and perhaps connectivity test?
    for key in mandatory_keys:
        if matched_dict.get(key) is None:
            logging.error(f"Missing {key}")
            return False
    return True
