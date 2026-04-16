import os
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def handle(request):
    try:
        return web.FileResponse('index.html')
    except:
        return web.Response(text="Bingo Ethiopia Live is Running")

async def on_startup(app):
    # Webhook ykn Polling kallaattiin akka hin banne
    print("Bot is starting...")
    asyncio.create_task(dp.start_polling())

async def create_app():
    app = web.Application()
    app.router.add_get('/', handle)
    app.on_startup.append(on_startup)
    return app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    web.run_app(create_app(), host='0.0.0.0', port=port)
