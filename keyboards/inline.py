from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def nav_keyboard(index: int, total: int) -> InlineKeyboardMarkup:
    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"gallery:{index - 1}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"gallery:{index + 1}"))

    navigation_row = buttons
    delete_row = [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{index}")]

    return InlineKeyboardMarkup(inline_keyboard=[navigation_row, delete_row])

