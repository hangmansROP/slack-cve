#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import slack


slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = slack.RTMClient(token=slack_token)
web_client = slack.WebClient(token=slack_token)


@rtm_client.run_on(event='message')
def bot_mentioned(**payload):
    data = payload['data']
    text = data['text']
    if ('<@{}>'.format(rtm_client.slack_bot_id)) in text:
        parse_query(text)


@rtm_client.run_on(event='hello')
def bot_connected(**payload):
    rtm_client.slack_bot_id = web_client.auth_test()['user_id']
    print('Bot {} connected to RTM!'.format(rtm_client.slack_bot_id))


def parse_query(text):
    accepted_commands = [
        'search',
        'vendor',
        'latest']
    user_query = text.split(" ")
    command = user_query[1]

    if command not in accepted_commands:
        print("Command {} not found!".format(command))


def main():
    print("Starting Slackbot!")
    rtm_client.start()


if __name__ == '__main__':
    main()
