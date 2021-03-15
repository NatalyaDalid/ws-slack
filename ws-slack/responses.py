import json
import logging
import slack_actions
from ws_sdk.web import WS


class Report:
    MANDATORY_V = ['ws_user_key', 'ws_org_token', 'ws_scope_token']

    def __init__(self,
                 pipeline_req,
                 config):
        self.config = config
        self.pipeline_req = pipeline_req
        self.ws_connector = WS(url=pipeline_req['ws_url'],
                               user_key=pipeline_req['ws_user_key'],
                               token=pipeline_req['ws_org_token'])
        self.execute()


class LibVulnerabilities(Report):
    def execute(self):
        if self.is_valid_request(self.pipeline_req):
            libs = self.ws_connector.get_vulnerabilities_per_lib(token=self.pipeline_req['ws_scope_token'])
            scope_type = self.ws_connector.get_scope_type_by_token(token=self.pipeline_req['ws_scope_token'])
            scope_name = self.ws_connector.get_scope_name_by_token(token=self.pipeline_req['ws_scope_token'])
            channel = self. get_channel_name(scope_type=scope_type, scope_token=self.pipeline_req['ws_scope_token'])

            header_text = f"{scope_type} {scope_name} Library Vulnerability report"
            block = self.create_lib_vul_block(header_text, libs)
            slack_actions.send_to_slack(channel=channel, block=json.dumps(block))
            logging.info("Sent lib vulnerabilities")
            return "OK"
        else:
            raise KeyError("Missing parameters")

    # In slack Channel names can’t contain spaces, periods, or most punctuation
    def get_channel_name(self, scope_type, scope_token):
        return f"{self.config['ChannelPrefix']}_{scope_type}_{self.ws_connector.get_scope_name_by_token(token=scope_token)}" \
            .lower().replace(" ", "_").replace(".", "_")

    def is_valid_request(self, conn_dict):        # TODO: Add syntax validation and perhaps connectivity test?
        for key in self.MANDATORY_V + ['ws_scope_token']:
            if conn_dict.get(key) is None:
                return False
        return True

    def create_lib_vul_block(self, header_text, libs) -> list:
        block = [self.create_header_block(header_text),
                 self.create_mrkdn_block(f"Found {len(libs)} libs with vulnerabilities")
                 ]
        for lib in libs:
            block.append(self.create_lib_vul_section(lib))
            # block.append({"type": "divider"})

        return block

    def create_lib_vul_section(self, lib) -> dict:  # TODO: CONTINUE WORKING ON MESSAGE
        elements = [{"type": "mrkdwn",
                     "text": f"<{lib['lib_url']}|{lib['filename']}> "
                             f"{self.print_set(lib['vulnerabilities'])}"
                     }]

        return {"type": "context",
                "elements": elements}

    def create_header_block(self, header) -> dict:
        return {"type": "header",
                "text": {"type": "plain_text",
                         "text": header,
                         "emoji": True}
                }

    def create_mrkdn_block(self, string) -> dict:
        return {"type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{string}"
                }
                }

    def get_sev_icon(self, severity) -> str:
        return {
            "high": "https://i.imgur.com/7h75Aox.png",
            "medium": "https://i.imgur.com/MtPw8GH.png",
            "low": "https://i.imgur.com/4ZJPTpS.png"
        }[severity]

    def create_vul_section(self, vul, org_details, conn_dict) -> dict:
        lib = vul['library']
        elements = [{"type": "image",
                     "image_url": self.get_sev_icon(vul['severity']),
                     "alt_text": "Severity"
                     },
                    {
                        "type": "mrkdwn",
                        "text": f"<{conn_dict['wss_url']}/Wss/WSS.html#!securityVulnerability;id={vul['name']};orgToken={org_details['orgToken']}|{vul['name']}> - "
                                f"<{conn_dict['wss_url']}/Wss/WSS.html#!libraryDetails;uuid={lib['keyUuid']};orgToken={org_details['orgToken']}|{lib['filename']}>\n"
                                f"*Product:* {vul['product']} *Project:* {vul['project']} *Score:* {vul['score']}"
                        # TODO CONVERT PROD/PROJ to URLs?
                    }
                    ]

        return {"type": "context",
                "elements": elements}

    def print_set(self, set_to_p) -> str:
        max_e_per_set = 3
        ret = []
        if len(set_to_p) < max_e_per_set:
            ret = ', '.join(set_to_p)
        else:
            for i, val in enumerate(set_to_p):
                if i < max_e_per_set:
                    ret.append(val)
                else:
                    break
            ret = ', '.join(ret) + " ..."

        return ret
