from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.crud import Crud

async def on_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Список книг", callback_data="list_books"), KeyboardButton(text="Заказы", callback_data="list_orders")],
        [KeyboardButton(text="Контакты", callback_data="contacts"), KeyboardButton(text="Поддержка", callback_data="support")]
    ])
    return kb

async def back_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="start")]
    ])
    return kb

async def cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="start")]
    ])
    return kb

async def book_info_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Описание", callback_data="description")],
        [InlineKeyboardButton(text="Купить книгу", callback_data="buy_book")],
        [InlineKeyboardButton(text="Назад к каталогу", callback_data="list_books")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    return kb

async def accept_order_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Принять заказ", callback_data="accept_order")],
        [InlineKeyboardButton(text="Отказ", callback_data="decline_order")]
    ])
    return kb

