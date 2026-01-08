import enum

from faststream.rabbit import RabbitBroker

from app.config import get_config, RabbitMQConfig


class ReminderMessageType(str, enum.Enum):
    SET_ACTIVITIES = "SET_ACTIVITIES"


class MessagePublisher:
    """ Message publisher class for RabbitMQ """
    REMINDER_QUEUE_NAME: str

    def __init__(self, rabbitmq_config: RabbitMQConfig):
        self.broker: RabbitBroker = RabbitBroker(url=rabbitmq_config.url)
        self.REMINDER_QUEUE_NAME: str = rabbitmq_config.reminder_queue_name
        self.reminder_publisher = self.broker.publisher(self.REMINDER_QUEUE_NAME)

    async def start(self):
        await self.broker.start()

    async def stop(self):
        await self.broker.stop()

    async def publish_set_activities_reminder(self, user_ids: list[int]):
        await self.reminder_publisher.publish(
            message={"user_id": user_ids, "type": ReminderMessageType.SET_ACTIVITIES},
            expiration=60 * 60,  # 1 hour
            persist=True,
        )



message_publisher = MessagePublisher(get_config().rabbitmq)
