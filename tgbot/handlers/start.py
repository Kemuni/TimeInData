from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def user_start(message: Message):
    await message.reply("Hello, World!")
