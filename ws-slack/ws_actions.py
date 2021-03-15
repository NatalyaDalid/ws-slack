import json
import logging

from ws_sdk.web import WS

f = open("cust_config.json", 'r')
cust_config = json.loads(f.read())

ws_cust_connector = WS(url=cust_config['ws_url'],
                       user_key=cust_config['ws_user_key'],
                       token=cust_config['ws_org_token'])


def is_email_exists(slack_email: str) -> bool:
    ws_user = None
    try:
        ws_users = ws_cust_connector.get_users()['users']
        ws_user = [user for user in ws_users if user['email'] == slack_email][0]
        logging.debug(f"Found name: {ws_user['name']} of email: {slack_email} in WS")
    except Exception:
        logging.exception("Error getting emails")

    return True if ws_user else False

