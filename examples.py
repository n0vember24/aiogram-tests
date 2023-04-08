import logging
from uuid import uuid4

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, RegexpCommandsFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, InputTextMessageContent, InlineQueryResultArticle, InlineQuery, ChatActions, \
    ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, KeyboardButton

from config import BOT_TOKEN

logging.basicConfig(level=logging.DEBUG)

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['buttons'])
async def buttons(msg: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    loc_btn = KeyboardButton('Location', request_location=True)
    pn_btn = KeyboardButton('Phone Number', request_contact=True)
    markup.add(loc_btn, pn_btn)
    await msg.reply('Buttons', reply_markup=markup)


@dp.message_handler(commands=['language'])
async def check_language(msg: Message):
    locale = msg.from_user.locale

    await msg.reply(md.text(
        md.bold('Info about your language:'),
        md.text('🔸', md.bold('Code:'), md.code(locale.language)),
        md.text('🔸', md.bold('Territory:'), md.code(locale.territory or 'Unknown')),
        md.text('🔸', md.bold('Language name:'), md.code(locale.language_name)),
        md.text('🔸', md.bold('English language name:'), md.code(locale.english_name)),
        sep='\n',
    ), ParseMode.MARKDOWN)


@dp.message_handler(RegexpCommandsFilter(regexp_commands=['start ([0-9]*)']))
async def send_welcome(msg: Message, regexp_command):
    await msg.reply(f"You have requested an item with id <code>{regexp_command.group(1)}</code>", ParseMode.HTML)


@dp.message_handler(commands='deeplink')
async def create_deeplink(msg: Message):
    bot_user = await bot.me
    bot_username = bot_user.username
    deeplink = f'https://t.me/{bot_username}?start={msg.from_user.id}'
    text = (
        f'Either send a command /item_1234 or follow this link {deeplink} and then click start\n'
        'It also can be hidden in a inline button\n\n'
        f'Or just send <code>/start {msg.from_user.id}</code>'
    )
    await msg.reply(text, disable_web_page_preview=True)


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()


@dp.message_handler(commands='/state')
async def cmd_start(msg: Message):
    await Form.name.set()
    await msg.reply("Добро пожаловать в наш бот!\nДля продолжения введите своё имя:")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await msg.reply('Действие отменено.', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text

    await Form.next()
    await msg.reply("Сколько вам лет?")


@dp.message_handler(lambda msg: not msg.text.isdigit(), state=Form.age)
async def process_age_invalid(msg: Message):
    return await msg.reply("Возраст пишется цифрами. Пожалуйста введите своё корректный возраст в виде числа.")


@dp.message_handler(lambda msg: msg.text.isdigit(), state=Form.age)
async def process_age(msg: Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(age=int(msg.text))

    # Configure ReplyKeyboardMarkup
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Мужик", "Женщина")
    markup.add("Транс")

    await msg.reply("Какой ваш пол?", reply_markup=markup)


@dp.message_handler(lambda msg: msg.text not in ["Мужик", "Женщина", "Транс"], state=Form.gender)
async def process_gender_invalid(msg: Message):
    return await msg.reply("Я пока что не знаю такого вида пола... Пожалуйста, введите корректный пол.")


@dp.message_handler(state=Form.gender)
async def process_gender(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = msg.text
        markup = ReplyKeyboardRemove()

        await bot.send_message(
            msg.chat.id,
            md.text(
                md.text('Я рад вас видеть,', md.bold(data['name'])),
                md.text('Ваш возраст:', md.code(data['age'])),
                md.text('Ваш пол:', data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    await state.finish()


@dp.message_handler()
async def start(msg: Message):
    # await ChatActions.typing(5)
    await ChatActions.upload_voice(1)
    await msg.reply(msg.text)


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    text = InputTextMessageContent(inline_query.query or 'Text')
    result_id = str(uuid4())
    item = InlineQueryResultArticle(id=result_id, title=f'Результаты запроса: {text}', input_message_content=text)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
