from typing import Dict

from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender

from api_parser import APIParser
from api_parser.types import ActivityTypes

router = Router(name=__name__)

ACTIVITY_TO_EMOJI: Dict[ActivityTypes, str] = {
    ActivityTypes.SLEEP: '🛏️',
    ActivityTypes.WORK: '💵',
    ActivityTypes.STUDY: '🏫',
    ActivityTypes.FAMILY: '👪',
    ActivityTypes.FRIENDS: '👥',
    ActivityTypes.RELAX: '💆‍♂️',
    ActivityTypes.SPORT: '💪',
    ActivityTypes.GAMES: '🎮',
}


@router.message(Command('summary'))
async def data_summary(message: types.Message, api: APIParser, bot: Bot):
    """ Send user's activities data summary """
    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
        users_data = await api.get_activities_summary(message.from_user.id)
        activity_string = '📊 Yours summary\n'
        for activity in users_data.data:
            activity_string += f'- <code>{activity.amount}</code> hours of {ACTIVITY_TO_EMOJI.get(activity.type_id, "")} <b>{activity.type_name.capitalize()}</b>'
            activity_string += f' \n'
        await message.answer(activity_string)
