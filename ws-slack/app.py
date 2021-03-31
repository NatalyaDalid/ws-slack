import inspect
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from slack_actions import *
from ws_actions import *
from ws_sdk import ws_utilities, ws_constants
import reports

# from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logging.getLogger('API').setLevel(logging.INFO)
logging.getLogger('slack_bolt').setLevel(logging.INFO)
logging.getLogger('slack_sdk').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)

f = open("config.json", 'r')
config = json.loads(f.read())

app = App()
app_handler = SlackRequestHandler(app)
api = FastAPI(title="WS For Slack")
# api.mount("/static", StaticFiles(directory="static"), name="static")


HOW_TO_USE_SLASH_BLOCK = f"""Usage: /ws4s <report name> <scope token>
                    Currently supported reports: {config['Reports']}
                    To get Scope tokens: /ws4s tokens <scope name> 
                    """                                                 # TODO MAKE THIS NICE BLOCK


class PipeLineRequest(BaseModel):
    ws_url: str
    ws_user_key: str
    ws_org_token: str
    ws_scope_token: Optional[str] = None


def authenticate_user(user_id: str):
    slack_email = get_slack_user_email(user_id)

    return is_email_exists(slack_email)


def parse_slash_syntax(message: dict) -> str:
    text = message.get('text')
    ret = ""
    logging.debug(f"Entered syntax: '{text}'")
    if text is None or not text:
        ret = HOW_TO_USE_SLASH_BLOCK
    else:
        command_list = list(message['text'].split())
        if len(command_list) == 2 and command_list[0].lower() == 'tokens':        # Retrieving tokens from report name
            scopes = ws_cust_connector.get_scopes(name=command_list[1])
            if len(scopes) == 0:
                ret = f"No Product or Project with the name: '{command_list[1]}' was found. Note that search is case sensitive"
                logging.debug(f"No scopes were found with name: {command_list[1]}")
            else:
                ret = f"{len(scopes)} scopes matches:"
                for scope in scopes:
                    line = f"Name: {scope['name']} Type: {scope['type']} Token: {scope['token']}"
                    if scope['type'] == ws_constants.PROJECT:
                        line = f"{line} Product: {scope['productName']}"
                    ret = ret + "\n" + line
                logging.debug(f"Found: {len(scopes)} scopes")
        elif len(command_list) == 2 \
                and command_list[0] in config['Reports'] \
                and ws_utilities.is_token(command_list[1]):      # Generating report
            logging.debug(f"Running report: {command_list[0]} on {command_list[1]}")

            ret = call_report(report_name=command_list[0],
                              conf_dict={"ws_scope_token": command_list[1]},
                              ws_connector=ws_cust_connector)
        else:
            ret = f"Entered syntax: '{text}' \n {HOW_TO_USE_SLASH_BLOCK}"
            logging.error(f"Invalid slash syntax: '{text}'")

    return ret


@app.command("/ws4s")
def slash_command(ack, say, command):
    logging.debug(f"Received Slash command with text: {command.get('text')}")
    ack()
    if authenticate_user(user_id=command['user_id']):
        ret_message = parse_slash_syntax(command)
        say(ret_message)
    else:
        text = "You are not authorized to access WhiteSource. Please check that your email Slack email address is the same in WhiteSource"
        say(text)
        logging.error(text)


@api.post("/slack/commands")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@api.get("/")
def hello():
    return "HOW TO USE THIS!"   # TODO FIX THIS


def call_report(report_name, conf_dict, ws_connector):
    if report_name not in config['Reports']:
        ret = f"Unsupported path: {report_name}"
    else:
        class_name = ''.join(word.title() for word in report_name.split('_'))          # Getting class name
        try:
            members = inspect.getmembers(reports, inspect.isclass)                     # Getting class itself
            cl = [m for m in members if m[0] == class_name][0][1]
            cl(ws_conn_details=conf_dict, ws_connector=ws_connector, config=config)    # Calling constructor of object
            ret = "OK"
        except KeyError:
            logging.exception("Error getting method")
            ret = "Error"

    return ret


@api.get("/fetch/{report_name}")
def catch_all(report_name: str,
              pipeline_req: PipeLineRequest,
              request: Request):
    if reports.is_valid_ws_conn_details(pipeline_req.__dict__):
        ret = call_report(report_name=report_name,
                          conf_dict=pipeline_req.__dict__,
                          ws_connector=WS(url=pipeline_req.__dict__['ws_url'],
                                          user_key=pipeline_req.__dict__['ws_user_key'],
                                          token=pipeline_req.__dict__['ws_org_token']))
    else:
        logging.error("Incorrect or WS connection details")
        ret = "Incorrect or WS connection details"

    return ret


def conf_validated():
    for key in config['MandatoryEnvVars']:
        try:
            val = os.environ[key]
            logging.debug(f"Started with env variables: {key}={val}")
        except KeyError:
            logging.error(f"Missing environment variable: {key}")
            return False

    return True


if __name__ == "__main__":
    if conf_validated():
        uvicorn.run(app="app:api", host="0.0.0.0", port=8000, reload=False, debug=True)
