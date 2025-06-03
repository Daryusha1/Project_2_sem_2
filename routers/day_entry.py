from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.fsm_day import DayEntry
from keyboards.main import cancel_keyboard, get_main_keyboard
from aiogram import F
from routers.gallery import send_entry
from pathlib import Path
import json

router = Router()

# 💛 Запись дня
@router.message(lambda msg: msg.text == "🌞 Записать день")
async def start_fsm(message: types.Message, state: FSMContext):
    await message.answer("💛 Какой цвет у твоего дня?", reply_markup=cancel_keyboard())
    await state.set_state(DayEntry.color)

# ❌ Отмена
@router.message(lambda msg: msg.text == "❌ Отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 Запись отменена", reply_markup=get_main_keyboard())

@router.message(lambda msg: msg.text == "🖼 Галерея")
async def show_gallery(message: types.Message):
    file_path = Path("storage/data.json")

    if not file_path.exists():
        await message.answer("У тебя пока нет записей 😔")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        await message.answer("Пока ничего не записано.")
        return

    entry = data[0]
    await send_entry(message.chat.id, entry, 0, len(data))

@router.message(DayEntry.color)
async def process_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer("👃 А какой запах у этого дня?")
    await state.set_state(DayEntry.smell)

@router.message(DayEntry.smell)
async def process_smell(message: types.Message, state: FSMContext):
    await state.update_data(smell=message.text)
    await message.answer("📝 Напиши слово дня или пришли голосом")
    await state.set_state(DayEntry.word)

@router.message(DayEntry.word)
async def process_word(message: types.Message, state: FSMContext):
    if message.text and not message.text.startswith("http"):
        await state.update_data(word={"type": "text", "value": message.text})
        await message.answer("🖼 Пришли фото дня")
        await state.set_state(DayEntry.photo)
    else:
        await message.answer("📝 Напиши слово дня в виде текста.")

@router.message(DayEntry.photo)
async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, пришли фотографию дня 📸")
        return

    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer("🎶 А теперь пришли музыку дня (аудио или ссылку)")
    await state.set_state(DayEntry.music)

@router.message(DayEntry.music)
async def process_music(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Музыка: либо аудио, либо ссылка
    if message.audio:
        user_data["music"] = {"type": "audio", "file_id": message.audio.file_id}
    elif message.text and message.text.startswith("http"):
        user_data["music"] = {"type": "link", "url": message.text}
    else:
        await message.answer("Пришли аудиофайл или ссылку на музыку 🎵")
        return

    # Завершение
    await message.answer("✅ День записан! Спасибо 🌷", reply_markup=get_main_keyboard())
    await state.clear()

    import json
    from pathlib import Path

    # Путь к файлу
    file_path = Path("storage/data.json")

    # Загружаем старые записи
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            all_entries = json.load(f)
    else:
        all_entries = []

    # Добавляем новую запись
    user_data["date"] = message.date.isoformat()
    user_data["user_id"] = message.from_user.id
    all_entries.append(user_data)

    # Сохраняем в файл
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print("💾 Запись сохранена в data.json")

@router.callback_query(F.data.startswith("delete:"))
async def delete_entry(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    file_path = Path("storage/data.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if index < 0 or index >= len(data):
        await callback.message.answer("❌ Такой записи не существует.")
        await callback.answer()
        return

    data.pop(index)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    await callback.answer("🗑 Запись удалена.")

    if not data:
        await callback.message.answer("🕳 Все записи удалены.")
        return

    new_index = max(0, index - 1)
    await send_entry(callback.message.chat.id, data[new_index], new_index, len(data))

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
    await message.answer("📆 Введи дату в формате `ДД.ММ.ГГГГ`, например: 01.06.2025", parse_mode="Markdown")
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

    # Поиск записи
    for i, entry in enumerate(data):
        entry_date = datetime.fromisoformat(entry["date"]).date()
        if entry_date == target_date:
            await state.clear()
            from routers.gallery import send_entry
            await send_entry(message, entry, i, len(data))
            return

    await message.answer("В этот день записей не найдено.")
    await state.clear()
