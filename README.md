![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub release](https://img.shields.io/github/release/whitesource-ps/wss-template.svg)](https://github.com/whitesource-ps/wss-template/releases/latest)  
# WhiteSource Slack Integration 
Tool that mediates between WS and Slack.

The tool can run as a docker container for easy deployment.

The tool supports:
* Accepting endpoint requests (e.g. from pipelines): 
  `https://<URL>/fetch/<REPORT_NAME>`
  
    The request body should contain:

    ```
   {
    "ws_user_key" : "<userKey>",
    "ws_org_token": "<orgToken>",
    "ws_url": "saas",
    "key": "<value>"...
   }
    ```
* Accepting Slack slash commands (/ws4s).
    
    Supported commands
    * /ws4s token <SCOPE NAME> - Get token ids
    * /ws4s <REPORT NAME> <TOKEN>

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu, RedHat
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
1. Python WS-SDK (installed in the Docker container)
1. Create Custom app in [Slack API](https://api.slack.com/apps?new_app=1) with the following permissions:
    * Slash commands:
        * Command: /ws4s
        * Request URL: https://<PUBLIC URL>/slack/commands
        * Short Description: Router for ws4S
        * Usage Hint: Report Scope_Name
        * Escape channels, users, and links sent to your app: Checked
    * Bots:
        * App Display Name:
            * Display Name: WS4S
            * Default username: ws4s




## Installation
1. Download or build ws-sdk wheel package.
1. Download or build ws-slack wheel package.    
1. Execute:


## Docker run instructions:
```
docker run -p 8000:8000 -e SLACK_BOT_TOKEN=xoxb-<TOKEN> -eSLACK_SIGNING_SECRET=<SECRET> ws-slack --name <CONTAINER_NAME>
```
