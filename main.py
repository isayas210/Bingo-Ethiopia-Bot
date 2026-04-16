import logging
from aiogram import Bot, Dispatcher, executor

# Token kee isa sirrii
API_TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    # Webhook moofaa qulqulleessuun Conflict ni balleessa
    await bot.delete_webhook()
    print("Bot-ni Bingo hojii jalqabeera!")

if __name__ == '__main__':
    # skip_updates=True ergaawwan conflict uuman bira darba
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
