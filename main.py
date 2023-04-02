import logging
from uuid import uuid4

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, InputTextMessageContent, InlineQueryResultArticle, InlineQuery

from config import BOT_TOKEN

logging.basicConfig(level=logging.DEBUG)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def start(msg: Message):
    await msg.reply(msg.text)


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    text = InputTextMessageContent(inline_query.query or 'Text')
    result_id = str(uuid4())
    item = InlineQueryResultArticle(id=result_id, title=f'Результаты запроса: {text}', input_message_content=text)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


if __name__ == '__main__':
    executor.start_polling(dp)
