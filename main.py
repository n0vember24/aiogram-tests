import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def start(msg: Message):
    await msg.reply(msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
