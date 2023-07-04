# mastodon-post-to-slack

🐘 Send Mastodon post to Slack channel

Mastodon does support RSS feed natively. However, Slack RSS integration posts all profile URLs in the conversation and their status URL, which occupy a large area in the channel, and its body text is always duplicated.

This Python application solves the issues by cleaning up the text and including only needed links in the post.

## Screenshot
Sample post from [@ThePSF@fosstodon.org](https://fosstodon.org/@ThePSF):

<img width="800" alt="Screenshot" src="https://user-images.githubusercontent.com/1425259/209457514-e3ad6c17-23c2-40ef-9115-8aa839195032.png">

## Usage

- Set up the incoming webhook integration on Slack.
- Create `.env` from `.env.sample` and `config.yaml` from `config.yaml.sample`.
- Install dependencies and run `main.py` as follows:

```shell
python3 -m vnev .venv
. .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Configuration

You can easily customize the source accounts and target Slack channels by `config.yaml`:

```yaml
---
feeds:
  - domain: mastodon.social
    username: mastodon
    channel: general
  - domain: fosstodon.org
    username: ThePSF
    channel: feed-python
    type: with_replies
```
