from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот «Ощущения дня».\n\nЯ помогу тебе сохранить настроение, запах, цвет, фото и музыку каждого дня. Готова начать?",
        reply_markup=get_main_keyboard()
    )
