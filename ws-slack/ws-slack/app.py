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
    f = open(f'{os.environ.get("WSS_CONF")}', 'r')
    conf = json.loads(f.read())
    ws_connector = WS(api_url=conf['wssApiUrl'], user_key=conf['wssUserKey'], token=conf['wssOrgToken'])
except FileNotFoundError | json.JSONDecodeError | KeyError:
    logging.exception("Error parsing configuration")
    exit

client = WebClient(token=conf['slackBotToken'])


@flask_app.route("/")
def hello():
    return "TBD HOW TO USE THIS!"   # TODO FIX THIS


def is_valid_request(conn_dict):        # TODO: Add syntax validation and perhaps connectivity test?
    for key in ['user_key', 'wss_url', 'wss_url']:
        try:
            conn_dict[key]
        except TypeError or KeyError | TypeError:
            return False
    return True


@flask_app.route("/fetch_lib_vulnerabilities", methods=["GET"])
def fetch_lib_vulnerabilities():
    conn_dict = request.get_json()

    if is_valid_request(conn_dict):
        libs = ws_connector.get_vulnerabilities_per_lib(token=conn_dict['scope_token'])
        scope_type = ws_connector.get_scope_type_by_token()
        org_details = ws_connector.get_organization_details()
        channel = f"{conf['channelPrefix']}_{scope_type}_{ws_connector.get_scope_name_by_token(token=conn_dict['scope_token'])}" \
            .lower().replace(" ", "_")

        send_block(json.dumps(SlackActions.create_lib_vul_block(scope_type, org_details, libs, conn_dict)))
        logging.info("Sent lib vulnerabilities")

        return "OK"
    else:
        return "Missing parameters"


def fetch_channels():
    try:
        result = client.conversations_list()
    except SlackApiError as e:
        logging.error(f"Error fetching channels: {e}")

    return result.__dict__['data']['channels']


def is_channel_exists(channel_name):
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
    except SlackApiError as e:
        logging.error(f"Error creating channels: {e}")
    c_data_dict = c.__dict__['data']['channel']
    r = client.conversations_join(channel=c_data_dict['id'])
    logging.debug(f"Channel created: {c_data_dict['name']} ID: {c_data_dict['id']}")


def send_block(channel, block):
    if not is_channel_exists(channel):
        create_channel(channel)
    try:
        client.chat_postMessage(channel=channel, blocks=block)
    except SlackApiError as e:
        logging.error(f"Got an error: {e.response['error']}")


class SlackActions:
    pass
