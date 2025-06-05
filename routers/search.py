from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.search_day import SearchDay
from keyboards.main import get_main_keyboard
from datetime import datetime
from pathlib import Path
import json

router = Router()

@router.message(lambda msg: msg.text == "📅 Найти по дате")
async def ask_date(message: types.Message, state: FSMContext):
    await message.answer("Введи дату в формате `ДД.ММ.ГГГГ`, например: 01.06.2025", parse_mode="Markdown")
    await state.set_state(SearchDay.waiting_for_date)

@router.message(SearchDay.waiting_for_date)
async def search_by_date(message: types.Message, state: FSMContext):
    try:
        target_date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("⚠️ Неверный формат. Попробуй ещё раз: `ДД.ММ.ГГГГ`")
        return

    file_path = Path("storage/data.json")
    if not file_path.exists():
        await message.answer("У тебя пока нет записей.")
        await state.clear()
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, entry in enumerate(data):
        entry_date = datetime.fromisoformat(entry["date"]).date()
        if entry_date == target_date:
            await state.clear()
            from routers.gallery import send_entry
            await send_entry(message, entry, i, len(data))
            return

    await message.answer("В этот день записей не найдено.")
    await state.clear()
