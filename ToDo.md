## Content
* Add reports

## UI
* Add welcome HTML screen

## Slash Functionality
* 


#### How to Build Docker image
1. Create ws-sdk wheel package (C:\GIT\whitesource-ps\ws_sdk\dist)
1. Execute:
```
cd C:\GIT\whitesource-ps
docker build -f ws-slack/Dockerfile -t ws-slack .
```

#### How to run Docker
```
docker run -p 8000:8000 -e SLACK_BOT_TOKEN=xoxb-<TOKEN> -eSLACK_SIGNING_SECRET=<SECRET> ws-slack --name <CONTAINER_NAME>
```
