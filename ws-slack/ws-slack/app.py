import json
import logging
import os
import sys
from flask import Flask, request
from slack_sdk.errors import SlackApiError
from ws_sdk.web import WS
from slack_sdk import WebClient

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
flask_app = Flask(__name__)
flask_app.config.from_object(os.environ['APP_SETTINGS'])

try:
    # f = open(f'{os.environ.get("WSS_CONF")}', 'r')
    # conf = json.loads(f.read())
    ws_connector = WS(url=flask_app.config['WS_URL'],
                      user_key=flask_app.config['WS_USER_KEY'],
                      token=flask_app.config['WS_ORG_TOKEN'])
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    logging.exception("Error parsing configuration")

client = WebClient(token=flask_app.config['SLACK_BOT_TOKEN'])


def is_valid_request(conn_dict):        # TODO: Add syntax validation and perhaps connectivity test?
    for key in ['user_key', 'wss_url', 'wss_url']:
        try:
            conn_dict[key]
        except (TypeError, KeyError, TypeError):
            return False
    return True


# In slack Channel names can’t contain spaces, periods, or most punctuation
def get_channel_name(scope_type, scope_token):
    return f"{flask_app.config['CHANNEL_PREFIX']}_{scope_type}_{ws_connector.get_scope_name_by_token(token=scope_token)}" \
        .lower().replace(" ", "_").replace(".", "_")


@flask_app.route("/")
def hello() -> str:
    return "TBD HOW TO USE THIS!"   # TODO FIX THIS


@flask_app.route("/<path>", methods=["GET"])
def catch_all(path):
    if path in flask_app.config['REPORTS']:
        try:
            method = globals()[path]
            return method(request.get_json())
        except KeyError:
            logging.exception("Error getting method")
    else:
        return f"Unsupported path: {path}"


def fetch_lib_vulnerabilities(conn_dict):
    if is_valid_request(conn_dict):
        libs = ws_connector.get_vulnerabilities_per_lib(token=conn_dict['scope_token'])
        scope_type = ws_connector.get_scope_type_by_token(token=conn_dict['scope_token'])
        scope_name = ws_connector.get_scope_name_by_token(token=conn_dict['scope_token'])
        channel = get_channel_name(scope_type=scope_type, scope_token=conn_dict['scope_token'])
        header_text = f"{scope_type} {scope_name} Library Vulnerability report"
        block = create_lib_vul_block(header_text, libs)
        send_to_slack(channel=channel, block=json.dumps(block))
        logging.info("Sent lib vulnerabilities")
        return "OK"
    else:
        return "Missing parameters"


def create_lib_vul_block(header_text, libs) -> list:
    block = [create_header_block(header_text),
             create_mrkdn_block(f"Found {len(libs)} libs with vulnerabilities")
             ]
    for lib in libs:
        block.append(create_lib_vul_section(lib))
        # block.append({"type": "divider"})

    return block


def create_lib_vul_section(lib) -> dict:  # TODO: CONTINUE WORKING ON MESSAGE
    elements = [{"type": "mrkdwn",
                 "text": f"<{lib['lib_url']}|{lib['filename']}> "
                         f"{print_set(lib['vulnerabilities'])}"
                 }]

    return {"type": "context",
            "elements": elements}


def create_header_block(header) -> dict:
    return {"type": "header",
            "text": {"type": "plain_text",
                     "text": header,
                     "emoji": True}
            }


def create_mrkdn_block(string) -> dict:
    return {"type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{string}"
            }
            }


def fetch_channels() -> list:
    try:
        result = client.conversations_list()
    except SlackApiError as e:
        logging.error(f"Error fetching channels: {e}")

    return result.__dict__['data']['channels']


def is_channel_exists(channel_name) -> bool:
    channel_exist = False
    channels = fetch_channels()
    for cur_channel in channels:
        if channel_name == cur_channel['name']:
            channel_exist = True
            logging.debug(f"Channel {channel_name} found")
            break
    logging.debug(f"Channel {channel_name} was not found")

    return channel_exist


def create_channel(channel_name, create_private=False):  # TODO CHANGE TO PRIVATE CHANNELS. CURRENTLY GET LIST THEM: https://stackoverflow.com/questions/53736333/slack-conversations-list-method-does-not-list-all-the-channels
    try:
        c = client.conversations_create(name=channel_name, is_private=create_private)
        c_data_dict = c.__dict__['data']['channel']
        r = client.conversations_join(channel=c_data_dict['id'])
        logging.debug(f"Channel {c_data_dict['name']} (ID: {c_data_dict['id']}) created ")
    except SlackApiError:
        logging.exception("Failed to create channel")


def send_to_slack(channel, block):
    if not is_channel_exists(channel):
        create_channel(channel)
    try:
        client.chat_postMessage(channel=channel, blocks=block)
    except SlackApiError as e:
        logging.exception("Unable to post to Slack")


def get_sev_icon(severity) -> str:
    return {
        "high": "https://i.imgur.com/7h75Aox.png",
        "medium": "https://i.imgur.com/MtPw8GH.png",
        "low": "https://i.imgur.com/4ZJPTpS.png"
    }[severity]


def create_vul_section(vul, org_details, conn_dict) -> dict:
    lib = vul['library']
    elements = [{"type": "image",
                 "image_url": get_sev_icon(vul['severity']),
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


def print_set(set_to_p) -> list:
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

