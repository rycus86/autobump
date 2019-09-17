import requests
from docker_helper import read_configuration


def send_message(message):
    webhook_url = read_configuration('SLACK_WEBHOOK', '/var/secrets/autobump', None)
    if not webhook_url:
        return

    icon_url = read_configuration('SLACK_ICON', '/var/secrets/autobump', None)

    requests.post(
        webhook_url,
        json=dict(channel='monitoring', text=message, username='autobump', icon_url=icon_url)
    )
