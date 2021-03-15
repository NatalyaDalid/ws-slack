import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from responses import *
from slack_actions import *
from ws_actions import *

# from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
f = open("config.json", 'r')
config = json.loads(f.read())

app = App()
app_handler = SlackRequestHandler(app)
api = FastAPI(title="WS For Slack")
# api.mount("/static", StaticFiles(directory="static"), name="static")


class PipeLineRequest(BaseModel):
    ws_url: str
    ws_user_key: str
    ws_org_token: str
    ws_scope_token: Optional[str] = None


def authenticate_user(user_id: str):
    slack_email = get_slack_user_email(user_id)

    return is_email_exists(slack_email)


def parse_slash_syntax():
    pass


@app.command("/ws4s")
def slash_command(ack, say, command):
    logging.debug(f"Received Slash command with text: {command.get('text')}")
    ack()
    if authenticate_user(user_id=command['user_id']):
        tmp = parse_slash_syntax()
        call_report()
    else:
        say("You are not authorized to access WhiteSource. Please check that your email Slack email address is the same in WhiteSource")
        # logging.error("User has no permissions to access WhiteSource")


@api.post("/slack/commands")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@api.get("/")
def hello():
    return "HOW TO USE THIS!"   # TODO FIX THIS


def call_report(report_name, req):
    if report_name in config['Reports']:
        class_name = ''.join(word.title() for word in report_name.split('_'))  # Getting class name
        try:
            cl = globals()[class_name]  # Getting class
            cl(req, config)  # Calling constructor
            return "OK"
        except KeyError:
            logging.exception("Error getting method")
    else:
        return f"Unsupported path: {report_name}"


@api.get("/fetch/{report_name}")
def catch_all(report_name: str,
              pipeline_req: PipeLineRequest,
              request: Request,
              ):
    return call_report(report_name, pipeline_req.__dict__)

    # if report_name in config['Reports']:
    #     class_name = ''.join(word.title() for word in report_name.split('_'))   # Getting class name
    #     try:
    #         cl = globals()[class_name]                                          # Getting class
    #         cl(pipeline_req.__dict__, config)                                   # Calling constructor
    #         return "OK"
    #     except KeyError:
    #         logging.exception("Error getting method")
    # else:
    #     return f"Unsupported path: {report_name}"


if __name__ == "__main__":
    uvicorn.run(app="app:api", host="0.0.0.0", port=8000, reload=False, debug=True)
