import logging

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerProducerMixin

from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_logger(name):
    return logging.getLogger(name)


class BaseWorker(ConsumerProducerMixin):
    def __init__(self):
        self.connection = Connection(settings.RABBIT_URL)
        self.exchange = Exchange('events', type='direct')
        self.queues = [
            Queue('response', exchange=self.exchange, routing_key='response'),
            Queue('gpt', exchange=self.exchange, routing_key='gpt'),
            Queue('tts', exchange=self.exchange, routing_key='tts'),
            Queue('stt', exchange=self.exchange, routing_key='stt'),
        ]

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=[self.queues[0]],
            callbacks=[self.process_message],
            prefetch_count=1
        )]

    def send_message(self, routing_key, message):
        self.producer.publish(
            body=message,
            exchange=self.exchange,
            routing_key=routing_key,
        )

    def process_message(self, body, message):
        self.on_message(body, message)
        message.ack()
