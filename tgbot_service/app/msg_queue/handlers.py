from faststream.rabbit import RabbitRouter
from loguru import logger

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.config import get_config
from app.msg_queue.types import ReminderRabbitMessage, ReminderMessageType
from app.msg_queue.tasks.notify_users import send_bunch_messages

router = RabbitRouter()

@router.subscriber(get_config().rabbitmq.reminder_queue_name)
async def handle_notify_users(message: ReminderRabbitMessage):
    logger.info(
        f'Received notification message: type="{message.type}", User IDs({len(message.user_ids)} users)={message.user_ids}'
    )
    if message.type == ReminderMessageType.SET_ACTIVITIES:
        logger.info(f'Sending "SET ACTIVITIES" notification to {len(message.user_ids)} users...')

        if get_config().miniapp_url:
            miniapp_kb_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Set activity in MiniApp",
                            web_app=WebAppInfo(url=get_config().miniapp_url)
                        )
                    ]
                ]
            )
        else:
            miniapp_kb_markup = None

        await send_bunch_messages(
            message.user_ids,
            "👋 Hey! It's time to set your activity!\n Type /set_activity command",
            keyboard_markup=miniapp_kb_markup
        )
        logger.info(f'Successfully sent "SET ACTIVITIES" notification to {len(message.user_ids)} users!')
