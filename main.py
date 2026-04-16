import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiohttp import web

# TOKEN kee Environment Variable Render irraa fudhata
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Mini App akka banamuuf (index.html tajaajila)
async def handle(request):
    try:
        return web.FileResponse('index.html')
    except:
        return web.Response(text="Bingo Ethiopia Live is Running")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render "PORT" nuuf kenna, yoo dhabame 10000 fayyadama
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Web server bota wajjiin akka dammaqu godha
    loop.create_task(start_web_server())
    # Bota kee kaasi
    executor.start_polling(dp, skip_updates=True)
