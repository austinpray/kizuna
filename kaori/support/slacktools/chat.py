from functools import partial

from .message import format_slack_mention


def send(slack_client,
         channel: str,
         text: str = '',
         thread_ts: str = None,
         **kwargs
         ):
    """chat.postMessage to a channel"""

    if text:
        text_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text,
            }
        }
        blocks = kwargs.get('blocks')
        if blocks and isinstance(blocks, list):
            blocks.insert(0, text_block)
        else:
            blocks = [text_block]

        kwargs['blocks'] = blocks
        print(blocks)

    return slack_client.api_call("chat.postMessage",
                                 channel=channel,
                                 thread_ts=thread_ts,
                                 as_user=True,
                                 **kwargs)


def reply(slack_client, message: dict, text: str):
    """Takes a message from some channel and chat.postMessage some text back with a user mention prepended"""
    return slack_client.api_call("chat.postMessage",
                                 channel=message['channel'],
                                 text="{} {}".format(format_slack_mention(message['user']), text),
                                 as_user=True)


def send_factory(slack_client, channel: str):
    """Curried function for sending messages so you don't have to keep passing channel in."""
    return partial(send, slack_client, channel)


def send_ephemeral(slack_client, channel: str, user: str, text: str):
    """
    chat.postEphemeral to a channel and user

    https://api.slack.com/methods/chat.postEphemeral
    """
    return slack_client.api_call("chat.postEphemeral",
                                 channel=channel,
                                 user=user,
                                 text=text,
                                 as_user=True)


def send_ephemeral_factory(slack_client, channel: str, user: str):
    """Curried function for sending ephemeral messages so you don't have to keep passing channel and user in."""
    return partial(send_ephemeral, slack_client, channel, user)
