#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pycvesearch import CVESearch
import os
import time
import slack
import requests


slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = slack.RTMClient(token=slack_token)
web_client = slack.WebClient(token=slack_token)
cve = CVESearch()


@rtm_client.run_on(event='message')
def bot_mentioned(**payload):
    data = payload['data']
    if 'text' in data.keys():
        text = data['text']
        channel_id = data['channel']
        thread_ts = data['ts']
        if ('<@{}>'.format(rtm_client.slack_bot_id)) in text:
            parse_query(text, thread_ts, channel_id)


@rtm_client.run_on(event='hello')
def bot_connected(**payload):
    rtm_client.slack_bot_id = web_client.auth_test()['user_id']
    print('Bot {} connected to RTM!'.format(rtm_client.slack_bot_id))


def parse_query(text, thread, channel):
    accepted_commands = {
        'search': search_cve,
        'vendor': search_vendor,
        'latest': get_latest
        }
    user_query = text.split(" ")
    command = user_query[1]

    if command not in accepted_commands:
        print("Command {} not found!".format(command))
        post_im('Command not found! Please try again.', channel, thread)
    else:
        accepted_commands[command](channel, thread)


def search_cve(channel, thread):
    print("Searching for CVE")


def search_vendor(channel, thread):
    print("vendor")


def get_latest(channel, thread):
    post_im("Fetching the 30 most recent CVE's...", channel, thread)
    cve_list = cve.last()
    latest_cve = '\n'.join([
        "*%s*: %s" % (issue['id'], issue['references'][0]) for issue in cve_list]
    )
    post_im(latest_cve, channel, thread)


def post_im(msg, channel_id, thread):
    web_client.chat_postMessage(
        channel=channel_id,
        text=msg,
        mrkdwn=True,
        icon_emoji=':robot_face:')


def main():
    print("Starting Slackbot!")
    rtm_client.start()


if __name__ == '__main__':
    main()
