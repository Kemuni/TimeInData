from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger

from config import get_config


broker = RabbitBroker(url=get_config().rabbitmq.url)
faststream_app = FastStream(broker)


async def rabbitmq_startup():
    logger.info('RabbitMQ broker startup...')
    from msg_queue.handlers import router
    broker.include_router(router)
    logger.info('RabbitMQ router included!')

    await faststream_app.start()
    logger.info('RabbitMQ started!')

async def rabbitmq_shutdown():
    logger.info('RabbitMQ broker stoping...')
    await faststream_app.stop()
    logger.info('RabbitMQ broker stopped!')
