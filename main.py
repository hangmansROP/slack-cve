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


def cve_chunk_gen(cve_list, print_num):
    for i in range(0, len(cve_list), print_num):
        yield cve_list[i : i + print_num]


@rtm_client.run_on(event="message")
def bot_mentioned(**payload):
    data = payload["data"]
    if "text" in data.keys():
        text = data["text"]
        channel_id = data["channel"]
        thread_ts = data["ts"]
        if "<@{}>".format(rtm_client.slack_bot_id) in text:
            parse_query(text, thread_ts, channel_id)


@rtm_client.run_on(event="hello")
def bot_connected(**payload):
    rtm_client.slack_bot_id = web_client.auth_test()["user_id"]
    print("Bot {} connected to RTM!".format(rtm_client.slack_bot_id))


def parse_query(text, thread, channel):
    accepted_commands = {
        "search": search_cve,
        "vendor": search_vendor,
        "latest": get_latest,
    }
    user_query = text.split(" ")
    command = user_query[1]

    if command not in accepted_commands:
        print("Command {} not found!".format(command))
        post_im("Command not found! Please try again.", channel, thread)
    else:
        accepted_commands[command](user_query, channel, thread)


def search_cve(query, channel, thread):
    print("[+]Search for %s" % query[2])
    post_im("Looking for CVE's relating to %s" % query[2], channel, thread)
    result_data = cve.search(query[2])["data"]
    print("[+]%d results found!" % len(result_data))

    if len(query) < 4 or query[3].lower() != "all":
        post_im("Returning the top 10 results:", channel, thread)
        post_im(
            "\n".join(
                "*%s*: \n%s" % (issue["id"], ("\n".join(issue["references"])))
                for issue in result_data[0:10]
            ),
            channel,
            thread,
        )
        post_im("to get all results, try @CVEBot search <query> all", channel, thread)
    else:
        post_im("*Warning!* Returning all results!:", channel, thread)
        for issue in cve_chunk_gen(result_data, 10):
            cve_chunked_list = "\n".join(
                "*%s*: \n%s" % (cve["id"], ("\n".join(cve["references"])))
                for cve in issue
            )
            post_im(cve_chunked_list, channel, thread)


def get_latest(query, channel, thread):
    post_im("Fetching the 30 most recent CVE's...", channel, thread)
    cve_list = cve.last()
    latest_cve = "\n".join(
        ["*%s*: %s" % (issue["id"], issue["references"]) for issue in cve_list]
    )
    post_im(latest_cve, channel, thread)


def post_im(msg, channel_id, thread):
    web_client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread,
        blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": msg}}],
        mrkdwn=True,
        icon_url="https://miro.medium.com/max/700/1*51hwpAU3rZpq0VN0YjAEVQ.jpeg",
    )


def main():
    print("Starting Slackbot!")
    rtm_client.start()


if __name__ == "__main__":
    main()
