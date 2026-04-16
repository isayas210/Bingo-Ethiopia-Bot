import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import WebAppInfo

# Token kee isa ati naaf ergite
API_TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c'

# Logging qindaysuuf
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Yeroo bot-ni jalqabu webhook qulqulleessuuf
async def on_startup(dp):
    await bot.delete_webhook()
    print("---------------------------------")
    print("Bot-ni Bingo hojii jalqabeera!")
    print("---------------------------------")

# Ergaa Command /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # HUBADHU: Linkii HTML kee isa bareedaa Render irratti 'Static Site' uumte as galchi
    # Yoo ammaaf linkii hin qabdu ta'e kanumaan yaali
    web_app_url = "https://bingo-ethio.netlify.app" # Fakkeenyaaf
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(
        text="🎮 Bingo Taphadhu", 
        web_app=WebAppInfo(url=web_app_url)
    ))
    
    await message.answer(
        f"Baga nagaaan dhufte {message.from_user.first_name}!\n\n"
        "Bingo taphachuuf button 'Bingo Taphadhu' jedhu tuqi.",
        reply_markup=markup
    )

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
