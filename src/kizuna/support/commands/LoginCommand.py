from slacktools.chat import send_ephemeral_factory

from .BaseCommand import BaseCommand
from ..models.User import User
from ..utils import build_url
from config import KIZUNA_WEB_URL


class LoginCommand(BaseCommand):
    def __init__(self, make_session) -> None:
        help_text = "kizuna login - login to the web interface"

        super().__init__(name='login',
                         pattern='login$',
                         help_text=help_text,
                         is_at=True,
                         db_session_maker=make_session)

    def respond(self, slack_client, message, matches):
        send = send_ephemeral_factory(slack_client, message['channel'], message['user'])
        with self.db_session_scope() as session:
            user = User.get_by_slack_id(session, message['user'])

            if not user:
                return send("I don't have your users in the db. Prolly run 'kizuna refresh users' and if that still "
                            "doesn't fix it: Austin fucked up somewhere :^(")

            send(build_url(KIZUNA_WEB_URL, '/login', {'auth': user.get_token()}))