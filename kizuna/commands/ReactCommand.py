import itertools
from random import choice

import sqlalchemy.orm as orm

from config import KIZUNA_WEB_URL
from .BaseCommand import BaseCommand
from ..models import ReactionImageTag, User
from ..nlp import extract_possible_tags
from ..slack import slack_link, send_ephemeral_factory, send_factory
from ..utils import build_url


class ReactCommand(BaseCommand):
    def __init__(self, make_session, nlp) -> None:
        help_text = 'kizuna react - view available reaction images and tags\n' \
                    'kizuna react add - upload some reaction images\n' \
                    'kizuna tfw <text> - Send a reaction related to the text'
        self.nlp = nlp
        super().__init__(name='react',
                         pattern='(react(?:ion)?|tfw)(?: (.*))?$',
                         help_text=help_text,
                         is_at=True,
                         db_session_maker=make_session)

    def respond(self, slack_client, message, matches):
        send = send_ephemeral_factory(slack_client, message['channel'], message['user'])
        send_public = send_factory(slack_client, message['channel'])

        query = matches[1]
        if query:
            query = query.strip()

        with self.db_session_scope() as session:
            user = User.get_by_slack_id(session, message['user'])

            if not user:
                return send("I don't have your users in the db. Prolly run 'kizuna refresh users' and if that still "
                            "doesn't fix it: Austin fucked up somewhere :^(")

            def authenticated_path(path):
                return build_url(KIZUNA_WEB_URL, path, {'auth': user.get_token()})

            react_homepage_url = authenticated_path('/react')
            react_add_image_url = authenticated_path('/react/images/new')

            if not query:
                # kizuna react$
                return send(react_homepage_url)

            if query == 'add':
                # kizuna react add
                return send(react_add_image_url)

            # kizuna react <tag>
            def add_images_nag():
                add_images = slack_link('(Add Images)', react_add_image_url)
                view_images = slack_link('(View Images)', react_homepage_url)
                send("You can add some images though! {} {}".format(add_images, view_images))

            possible_tags = [token.text for token in extract_possible_tags(self.nlp, query)]

            tags = session \
                .query(ReactionImageTag) \
                .options(orm.joinedload("images")) \
                .filter(ReactionImageTag.name.in_(possible_tags)) \
                .all()

            if tags:
                images = list(itertools.chain.from_iterable([tag.images for tag in tags]))

                if len(images) > 0:
                    for image in images:
                        image.tags_text = [tag.name for tag in image.tags if tag.name in possible_tags]
                    images.sort(key=lambda t: len(t.tags_text), reverse=True)
                    best_match_length = len(images[0].tags_text)
                    best_matches = [image for image in images if len(image.tags_text) == best_match_length]
                    return send_public(choice(best_matches).url)

                send_public('I don\'t have any images for "{}" :^('.format(query))
                return add_images_nag()

            send_public('I don\'t have anything for "{}" :^('.format(query))
            return add_images_nag()
