from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto
import json
from pathlib import Path
from datetime import datetime

from config.settings import BOT_TOKEN
from aiogram import Bot
from keyboards.inline import nav_keyboard

router = Router()
bot = Bot(token=BOT_TOKEN)

# Показ первой записи
@router.message(Command("gallery"))
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
    await send_entry(message, entry, 0, len(data))


# Листание галереи
@router.callback_query(F.data.startswith("gallery:"))
async def navigate_gallery(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    file_path = Path("storage/data.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if index < 0 or index >= len(data):
        await callback.answer("⚠️ Запись не найдена")
        return

    entry = data[index]
    await send_entry(callback, entry, index, len(data))
    await callback.answer()


# Функция отправки или редактирования записи
async def send_entry(target, entry, index, total):
    date_obj = datetime.fromisoformat(entry["date"])
    date_text = date_obj.strftime("%d.%m.%Y")

    # Защита для слова
    word_text = "—"
    if "word" in entry and isinstance(entry["word"], dict):
        if entry["word"].get("type") == "text":
            word_text = entry["word"].get("value", "—")
        else:
            word_text = "(не в текстовом формате)"

    caption = f"🗓 Дата: {date_text}\n" \
              f"🟡 Цвет: {entry.get('color', '—')}\n" \
              f"👃 Запах: {entry.get('smell', '—')}\n" \
              f"📝 Слово: {word_text}\n"

    if "music" in entry and entry["music"].get("type") == "link":
        caption += f"🎵 Музыка: {entry['music'].get('url', '')}\n"

    keyboard = nav_keyboard(index, total)

    if isinstance(target, types.Message):
        await bot.send_photo(
            chat_id=target.chat.id,
            photo=entry.get("photo", ""),
            caption=caption,
            reply_markup=keyboard
        )
    elif isinstance(target, types.CallbackQuery):
        media = InputMediaPhoto(
            media=entry.get("photo", ""),
            caption=caption
        )
        await target.message.edit_media(media=media, reply_markup=keyboard)
@router.callback_query(F.data.startswith("delete:"))
async def delete_entry(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    file_path = Path("storage/data.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if 0 <= index < len(data):
        del data[index]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        await callback.message.delete()
        await callback.answer("✅ Запись удалена.")
    else:
        await callback.answer("⚠️ Не удалось удалить запись.")
