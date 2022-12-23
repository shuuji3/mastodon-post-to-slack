import json
import os

import feedparser
from htmlslacker import HTMLSlacker
import httpx

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
MASTODON_DOMAIN = os.environ['MASTODON_DOMAIN']
MASTODON_USERNAME = os.environ['MASTODON_USERNAME']


def make_payload(entry, username, icon_url):
    summary = HTMLSlacker(entry.summary).get_output()

    media_contents = entry.get('media_content')
    if media_contents:
        media_urls = '\n' + '\n'.join(media['url'] for media in media_contents)
    else:
        media_urls = ''

    text = f'''{summary}{media_urls}'''
    return json.dumps({"channel": SLACK_CHANNEL, "username": username, "icon_url": icon_url, "text": text})


def post(payload):
    r = httpx.post(SLACK_WEBHOOK_URL, data=payload)
    print(r.status_code, r.is_success, r.text)


def main():
    url = f'https://{MASTODON_DOMAIN}/@{MASTODON_USERNAME}.rss'
    data = feedparser.parse(url)

    user_id = f'{MASTODON_USERNAME}@{MASTODON_USERNAME}'
    username = f'{data.feed.title} ({user_id})'
    icon_url = data.feed.webfeeds_icon

    for entry in reversed(data.entries):
        payload = make_payload(entry, username, icon_url)
        post(payload)
        break


if __name__ == '__main__':
    main()
