from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import os

# Token kee Render irratti waan galchiteef asitti hin jijjiirin
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    
    # 1. Button Bilbila Gaafatu (Share Contact)
    contact_btn = KeyboardButton(text="📲 Lakkoofsa Bilbilaa Ergi", request_contact=True)
    
    # 2. Button Mini App (Bingo) - Link mini app keetii "url" irratti galchi
    bingo_btn = KeyboardButton(
        text="🎮 Bingo Taphadhu", 
        web_app=WebAppInfo(url="https://bingo-ethiopia.com") # Link kee asitti jijjiiri
    )
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(contact_btn).add(bingo_btn)
    
    msg = (f"Baga nagaan dhufte, {user_name}! 👋\n\n"
           "Tajaajila keenya guutummaatti argachuuf 'Lakkoofsa Bilbilaa Ergi' kan jedhu tuqi.")
    
    await message.answer(msg, reply_markup=keyboard)

# Lakk. Bilbilaa yoo ergan ofiin galmeessuuf
@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    phone = message.contact.phone_number
    await message.answer(f"✅ Galmeen kee milkaa'eera!\nBilbila: {phone}\nAmma 'Bingo Taphadhu' tuquun dorgomi.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
