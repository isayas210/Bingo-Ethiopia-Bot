import logging
from aiogram import Bot, Dispatcher, executor
from os import getenv

# API Token kee galchi
API_TOKEN = 'TOKEN_KEE_AS_GALCHI'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Akka bot-ni kee yeroo hunda kuta (Conflict) hin uumneef
async def on_startup(dp):
    await bot.delete_webhook() # Webhook moofaa qulqulleessa
    print("Bot-ni Bingo hojii jalqabeera!")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
