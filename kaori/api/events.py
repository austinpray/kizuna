import logging
import ujson as json

import falcon
from dramatiq.message import Message
from falcon import Request
from kaori.support.slacktools.authorization import verify_signature


class EventsResource(object):

    def __init__(self, config, rabbitmq_broker):
        self.config = config
        self.logger = logging.getLogger('kaori_api.' + __name__)
        self.rabbitmq_broker = rabbitmq_broker

    def on_post(self, req: Request, resp):

        go_away = json.dumps({'ok': False, 'msg': 'go away'})

        if not req.content_length:
            resp.status = falcon.HTTP_400
            resp.body = go_away
            return

        # defaults to utf8 but should probably look at http headers to get this value, charset and stuff
        body = req.bounded_stream.read().decode('utf8')

        try:
            if not verify_signature(signing_secret=self.config.SLACK_SIGNING_SECRET,
                                    request_timestamp=int(req.get_header('X-Slack-Request-Timestamp')),
                                    body=body,
                                    signature=req.get_header('X-Slack-Signature')):
                resp.status = falcon.HTTP_401
                resp.body = go_away
                return
        except ValueError as e:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'ok': False, 'msg': str(e)})
            return

        doc = json.loads(body)
        callback_type = doc['type']

        if callback_type == 'url_verification':
            resp.body = doc['challenge']
            return

        if callback_type == 'event_callback':
            self.logger.debug(doc)
            self.rabbitmq_broker.enqueue(Message(queue_name='default',
                                                 actor_name='slack_worker',
                                                 args=(doc,),
                                                 options={},
                                                 kwargs={}))

        resp.body = json.dumps({'ok': True, 'msg': 'thanks!'})
