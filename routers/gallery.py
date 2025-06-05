from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto
from config.settings import BOT_TOKEN
from aiogram import Bot
from keyboards.inline import nav_keyboard
from datetime import datetime
from pathlib import Path
import json

router = Router()
bot = Bot(token=BOT_TOKEN)

# Команда /gallery или кнопка "Галерея"
@router.message(Command("gallery"))
@router.message(lambda msg: msg.text == "🖼 Галерея")
async def show_gallery(message: types.Message):
    file_path = Path("storage/data.json")

    if not file_path.exists():
        await message.answer("У тебя пока нет записей 😔")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    user_data = [d for d in all_data if d.get("user_id") == message.from_user.id]

    if not user_data:
        await message.answer("Пока ничего не записано.")
        return

    entry = user_data[0]
    await send_entry(message, entry, 0, len(user_data))


# Листание галереи
@router.callback_query(F.data.startswith("gallery:"))
async def navigate_gallery(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    file_path = Path("storage/data.json")

    with open(file_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    user_id = callback.from_user.id
    user_data = [d for d in all_data if d.get("user_id") == user_id]

    if index < 0 or index >= len(user_data):
        await callback.answer("⚠️ Запись не найдена")
        return

    entry = user_data[index]
    await send_entry(callback, entry, index, len(user_data))
    await callback.answer()


# Удаление записи
@router.callback_query(F.data.startswith("delete:"))
async def delete_entry(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    file_path = Path("storage/data.json")

    with open(file_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    user_id = callback.from_user.id
    user_data = [d for d in all_data if d.get("user_id") == user_id]

    if 0 <= index < len(user_data):
        to_delete = user_data[index]
        all_data.remove(to_delete)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        await callback.message.delete()
        await callback.answer("✅ Запись удалена.")
    else:
        await callback.answer("⚠️ Не удалось удалить запись.")


# Отправка записи
async def send_entry(target, entry, index, total):
    date_obj = datetime.fromisoformat(entry["date"])
    date_text = date_obj.strftime("%d.%m.%Y")

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
