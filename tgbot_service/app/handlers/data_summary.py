from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender

from app.api_parser import APIParser
from app.types import ACTIVITY_TO_EMOJI

router = Router(name=__name__)


@router.message(Command('summary'))
async def data_summary(message: types.Message, api: APIParser, bot: Bot):
    """ Send user's activities data summary """
    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
        users_data = await api.get_activities_summary(message.from_user.id)
        activity_string = 'Yours summary 📊\n'
        for activity in users_data.data:
            activity_string += (
                f'- <code>{activity.hours_amount}</code> hours of '
                f'<b>{activity.activity_type.name.capitalize()}</b> {ACTIVITY_TO_EMOJI.get(activity.activity_type, "")}'
            )
            activity_string += f' \n'
        await message.answer(activity_string)
