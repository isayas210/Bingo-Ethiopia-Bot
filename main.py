import logging
import os
from aiogram import Bot, Dispatcher, executor

# Token kee isa sirrii
API_TOKEN = os.getenv('TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    # drop_pending_updates=True update-oota conflict uuman hunda ni haqas
    await bot.delete_webhook(drop_pending_updates=True)
    print("---------------------------------")
    print("Bot-ni Bingo Conflict malee jalqabeera!")
    print("---------------------------------")

if __name__ == '__main__':
    # skip_updates=True Conflict bira darbuuf baay'ee gargaara
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
