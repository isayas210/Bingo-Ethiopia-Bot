import logging
from aiogram import Bot, Dispatcher, executor

# Token kee
API_TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    # Webhook hunda ni qulqulleessa, update-oota duraan conflict uuman ni dhabamsiisa
    await bot.delete_webhook(drop_pending_updates=True)
    print("---------------------------------")
    print("Bot-ni Bingo hojii jalqabeera!")
    print("---------------------------------")

if __name__ == '__main__':
    # skip_updates=True Conflict balleessuuf ni gargaara
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
