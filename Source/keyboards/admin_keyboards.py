from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.crud import Crud

async def on_admin_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Управление книгами", callback_data="manage_books")],
        [KeyboardButton(text="Список заказов", callback_data="manage_orders")],
        [KeyboardButton(text="Список вопросов", callback_data="manage_questions")]
    ])
    return kb

async def manage_books_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить книгу", callback_data="add_book")],
        [InlineKeyboardButton(text="Удалить книгу", callback_data="delete_book")],
        [InlineKeyboardButton(text="Назад", callback_data="admin_start")]
    ])
    return kb