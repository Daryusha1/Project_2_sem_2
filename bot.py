from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN
from routers.start import router as start_router
from routers.day_entry import router as day_router
from routers.gallery import router as gallery_router
from routers.search import router as search_router

import logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(day_router)
dp.include_router(gallery_router)
dp.include_router(search_router)

if __name__ == '__main__':
    import asyncio
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    asyncio.run(main())
