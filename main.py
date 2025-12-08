import asyncio
from aiogram import Bot, Dispatcher, Router, types, BaseMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from routers.booking import booking_router
from db import create_pool
from menu import main_menu
from config import BOT_TOKEN
class DbPoolMiddleware(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event, data):
        data['db_pool'] = self.pool
        return await handler(event, data)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()
router = Router()
dp.include_router(router)
dp.include_router(booking_router)

@router.message(CommandStart())
async def start(message: types.Message):
    await message.reply('Выберите опцию', reply_markup=main_menu)
    # можно добавить функцию в зависимости от времени суток привествовать


async def main():
    pool = await create_pool()
    dp.message.middleware(DbPoolMiddleware(pool))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

