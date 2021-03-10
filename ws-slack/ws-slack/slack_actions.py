import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import config

client = WebClient(token=config.Shared['slackBotToken'])


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


def create_channel(channel_name, create_private=False): # TODO CHANGE TO PRIVATE CHANNELS. CURRENTLY GET LIST THEM: https://stackoverflow.com/questions/53736333/slack-conversations-list-method-does-not-list-all-the-channels
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
