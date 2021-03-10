import logging
from slack_bolt import App
from config import Shared

slack_app = App(
    token=Shared.conf['slackBotToken'],
    signing_secret=Shared.conf['slackSigningSecret']
)

SCOPE_TYPES = ["organization", "product", "project"]
REPORT_TYPES = ['lib_vulnerabilities']


@slack_app.command("/wss4slack")
def slash_command(ack, say, command):
    logging.debug(f"Received Slash command with text: {command.get('text')}")
    ack()
    try:
        say(f"WSS 4 Slack checking input: {command['text']}")     # TODO REMOVE
        input_list = list(command['text'].split())
        is_report = True if 'report' in input_list else False

        report_scope_f = filter(lambda s: s in SCOPE_TYPES, input_list)  # Getting scope name
        report_scope = list(report_scope_f).pop()
        scope_name = input_list[input_list.index(report_scope) + 1]
        dic = {scope_name: True}
        report_type_f = filter(lambda s: s in REPORT_TYPES, input_list)
        report_type = list(report_type_f).pop()
        scope_token = wss_api.get_scope_token_by_name(CONN_DICT['user_key'], CONN_DICT['org_token'], scope_name)
        CONN_DICT['scope_token'] = scope_token
        # Input validation
        if is_report is False:
            say("Unsupported operation. Currently supported: [report]")
        elif scope_token is None:
            say("Invalid scope name")
        elif report_scope is None:
            say(f"Invalid scope type. Currently supported: {SCOPE_TYPES}")
        elif report_type is None:
            say(f"Invalid report type. Currently supported: {REPORT_TYPES}")
        elif report_type == 'lib_vulnerabilities':
            fetch_lib_vulnerabilities(report_scope, CONN_DICT)
            return "SUCCESS"
    except KeyError:
        pass
    # Response in case that input syntax is missing or wrong
    webhook_url = command['response_url']
    webhook = WebhookClient(webhook_url)
    ret_block = [create_header_block("WSS 4 Slack"),
                 create_mrkdn_block("*Usage:* /wss4slack report [report type] organization/product/project [name]")]
    response = webhook.send(blocks=ret_block)
