import logging
import io

from PIL import Image
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ContentType, ParseMode
from rembg import remove

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(msg: Message):
    await msg.reply("Я рад видеть вас в нашем боту!")


# @dp.message_handler(content_types=ContentType.PHOTO)
# async def answer_to_photo(msg: Message):
#     in_img = msg.photo[-1]
#     down_img = await in_img.download(destination_file=f'input/{in_img.file_unique_id}.jpg')
#     bytes_img = io.BytesIO(down_img)
#     rem_img = Image.open(bytes_img)
#     out_img = remove(rem_img)
#     out_img.save(f'output/{in_img.file_unique_id}.jpg')


@dp.message_handler(content_types=ContentType.PHOTO)
async def answer_to_photo(msg: Message):
    inp_photo = msg.photo[-1]
    caption = f"File Unique ID: `{inp_photo.file_unique_id}`\n*Test Caption*"
    await msg.reply_photo(inp_photo.file_id, caption, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
