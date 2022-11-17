from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup,
)
from loguru import logger as lg
from db_crud import get_all_chains, add_chain_monitoring, init_db
from chain_api import monitoring_chains_for_user
from conf import Conf
import asyncio

lg.add("logs/tg_bot.log", level="DEBUG")

init_db()

# http://t.me/cosmo_proposals_bot
bot = Bot(token=Conf.tg_token)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

from aiogram.dispatcher.filters.state import State


class ExtState(State):
    async def set(self, user=None):
        """Option to set state for concrete user"""
        state = Dispatcher.get_current().current_state(user=user)
        await state.set_state(self.state)


class Form(StatesGroup):
    chain = ExtState()
    user_id = ExtState()


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    # await bot.send_message(msg.from_user.id, msg.text)
    await asyncio.get_running_loop().create_task(
        monitoring_chains_for_user(message.from_user.id)
    )


@dp.message_handler(commands=["add_chain"])
async def select_chain_monitoring(message: types.Message):
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    for ch in get_all_chains():
        kb.add(ch)

    await Form.chain.set()
    await message.reply(
        "select interest chain and press /start for monitoring", reply_markup=kb
    )
    await Form.user_id.set(user=message.from_user.id)


@dp.message_handler(state="*")
async def process_chain(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["chain"] = message.text
        data["user_id"] = message.from_user.id

    await state.finish()
    add_chain_monitoring(data["user_id"], data["chain"])
    lg.info(f'added {data["chain"]} for user {data["user_id"]}')


@dp.message_handler()
async def echo(message: types.Message):

    await message.answer(message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
