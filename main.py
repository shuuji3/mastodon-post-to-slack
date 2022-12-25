from dotenv import load_dotenv
import json
import os
import sqlite3
from datetime import datetime
from time import mktime
import yaml

import feedparser
from htmlslacker import HTMLSlacker
import httpx

load_dotenv()

SQLITE3_PATH = os.environ['SQLITE3_PATH']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def make_payload(entry, username, icon_url, channel):
    summary = HTMLSlacker(entry.summary).get_output()

    media_contents = entry.get('media_content')
    if media_contents:
        media_urls = '\n' + '\n'.join(media['url'] for media in media_contents)
    else:
        media_urls = ''

    text = f'''{summary}{media_urls}'''
    return json.dumps(
        {
            'channel': channel,
            'username': username,
            'icon_url': icon_url,
            'text': text,
        }
    )


def post_to_slack(payload):
    return httpx.post(SLACK_WEBHOOK_URL, data=payload)


def update_latest_post(
    connection: sqlite3.Connection,
    user_id: str,
    latest_status_id: str,
    published: datetime,
):
    cur = connection.cursor()
    cur.execute(
        '''
        insert into post(user_id, latest_status_id, published)
        values (?, ?, ?)
        on conflict(user_id) do update set
            user_id=?,
            latest_status_id=?,
            published=?
        where user_id=?
        ''',
        (
            user_id,
            latest_status_id,
            published,
            user_id,
            latest_status_id,
            published,
            user_id,
        ),
    )
    connection.commit()


def prepare_db(connection: sqlite3.Connection):
    cur = connection.cursor()
    cur.execute(
        '''
        create table if not exists post(
            user_id primary key,
            latest_status_id text,
            published text
        )  
        '''
    )
    connection.commit()


def is_new_post(connection: sqlite3.Connection, user_id, entry):
    cur = connection.cursor()
    post = cur.execute(
        '''
        select user_id, latest_status_id, published
        from post
        where user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    if post is None:
        return True
    else:
        user_id, latest_status_id, published = post
        return get_published_datetime(entry) > datetime.strptime(
            published, '%Y-%m-%d %H:%M:%S'
        )


def get_published_datetime(entry):
    return datetime.fromtimestamp(mktime(entry.published_parsed))


def main():
    con = sqlite3.connect(SQLITE3_PATH)
    prepare_db(con)

    config = yaml.load(open('config.yaml'), yaml.Loader)
    for feed in config['feeds']:
        domain = feed['domain']
        username = feed['username']
        channel = feed['channel']

        url = f'https://{domain}/@{username}.rss'
        data = feedparser.parse(url)

        user_id = f'{username}@{domain}'
        username = f'{data.feed.title} ({user_id})'
        icon_url = data.feed.webfeeds_icon

        for entry in reversed(data.entries):
            if not is_new_post(con, user_id, entry):
                continue

            payload = make_payload(entry, username, icon_url, channel)
            response = post_to_slack(payload)
            if response.is_success:
                published = get_published_datetime(entry)
                update_latest_post(con, user_id, entry.id, published)


if __name__ == '__main__':
    main()
