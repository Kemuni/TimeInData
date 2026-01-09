import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger

from app.config import get_config


broker = RabbitBroker(url=get_config().rabbitmq.url, logger=logging.getLogger(__name__))
faststream_app = FastStream(broker)


async def rabbitmq_startup():
    from app.msg_queue.handlers import router

    logger.info('RabbitMQ broker startup...')
    broker.include_router(router)
    logger.info('RabbitMQ router included!')

    await faststream_app.start()
    logger.info('RabbitMQ started!')

async def rabbitmq_shutdown():
    logger.info('RabbitMQ broker stoping...')
    await faststream_app.stop()
    logger.info('RabbitMQ broker stopped!')
