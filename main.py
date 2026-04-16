import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# TOKEN kee asitti galchi
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Mini App akka banamuuf (index.html tajaajila)
async def handle(request):
    if os.path.exists('index.html'):
        return web.FileResponse('index.html')
    return web.Response(text="Bingo Ethiopia is Running!")

async def on_startup(dp):
    # Web server port Render irratti jalqabsiisuu
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    print("Web server started on port 10000")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Baga nagaan dhufte! Mini App banuun taphadhu.")

if __name__ == '__main__':
    # Bota kaasuu
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(dp))
    executor.start_polling(dp, skip_updates=True)
