import os
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web

# TOKEN kee Environment Variable Render irraa fudhata
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def handle(request):
    try:
        # Mini App kee akka banamuuf
        return web.FileResponse('index.html')
    except:
        return web.Response(text="Bingo Ethiopia is Live!")

async def start_bot():
    # Conflict akka hin uumneef polling asitti jalqaba
    print("Bot dammaqaa jira...")
    await dp.start_polling()

async def create_app():
    app = web.Application()
    app.router.add_get('/', handle)
    # Bota server wajjin kaasa
    asyncio.create_task(start_bot())
    return app

if __name__ == '__main__':
    # Render port nuuf kenna
    port = int(os.environ.get("PORT", 10000))
    web.run_app(create_app(), host='0.0.0.0', port=port)
