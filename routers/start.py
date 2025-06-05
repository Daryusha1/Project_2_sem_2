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

from aiogram.filters import Command

@router.message(Command("help"))
async def help_handler(message: types.Message):
    text = (
        "🤖 *Бот «Ощущения дня»* помогает тебе сохранять:\n"
        "— цвет\n"
        "— запах\n"
        "— слово\n"
        "— фото\n"
        "— музыку (аудио или ссылку)\n\n"
        "📍 Команды и кнопки:\n"
        "`/start` — начать\n"
        "🌞 Записать день — внести своё состояние за день\n"
        "🖼 Галерея — просмотреть все записанные дни\n"
        "📅 Найти по дате — найти запись по определенному дню\n\n"
        "🗑 В галерее можно удалять записи.\n"
    )
    await message.answer(text, parse_mode="Markdown")

