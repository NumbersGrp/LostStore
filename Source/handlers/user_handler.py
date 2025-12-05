import datetime
import uuid
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from core.bot import dp, bot
from database.crud import Crud
from keyboards.user_keyboards import *
from aiogram import F
from states.effect import ChooseBook, OrderAnswer, AcceptOrder, Support
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import asyncio


crud = Crud()

ADMIN_IDS = crud.get_all_admins()
ADMIN_IDS = [admin.tid for admin in ADMIN_IDS]

WELCOME_TEXT = ''
BUY_TEXT = ''
HELP_TEXT = ''
with open("Source/content/welcome_text.txt", "r") as f:
    WELCOME_TEXT = f.read()
with open("Source/content/buy_text.txt", "r") as f:
    BUY_TEXT = f.read()
with open("Source/content/help_text.txt", "r") as f:
    HELP_TEXT = f.read()

@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None:
        crud.create_user(message.from_user.username, message.from_user.id, chat_id=message.chat.id)
    user = crud.get_user(message.from_user.id)
    await message.answer(WELCOME_TEXT, reply_markup=await on_start_kb())

@dp.callback_query(F.data == 'start')
async def back_handler(callback: CallbackQuery, state: FSMContext = None):
    await state.clear()
    await start_handler(callback.message, state)

# [KeyboardButton(text="Список книг", callback_data="list_books"), KeyboardButton(text="Заказы", callback_data="list_orders")],
# [KeyboardButton(text="Контакты", callback_data="contacts"), KeyboardButton(text="Поддержка", callback_data="support")]

#CHOOSE BOOK SEQUENCE
@dp.message(F.text.lower() == 'список книг')
async def list_books(message: Message, state: FSMContext = None):
    i=1
    books = crud.get_all_books()
    text = "📚Список книг:\n"
    if books == None:
        await message.answer("Список книг пуст.")
        return
    for book in books:
        text += f"{i}. {book.title}\n"
        text += f"👤 {book.author}\n"
        text += f"🔸 {book.price}\n"
        text += f"📂 {book.category}\n\n"
        i+=1
    text+="Введите цифру чтобы узнать больше о книге"
    await message.answer(text, reply_markup=await back_kb())
    await state.set_state(ChooseBook.book_id)

@dp.callback_query(F.data == 'list_books')
async def list_handler(callback: CallbackQuery, state: FSMContext = None):
    await state.clear()
    await list_books(callback.message, state)

@dp.message(StateFilter(ChooseBook.book_id))
async def choose_book(message: Message, state: FSMContext = None):
    book_id = (message.text or "").strip()
    await state.update_data(book_id=book_id)
    if not book_id:
        await message.answer("Номер книги не может быть пустым. Введите номер книги:")
        return
    books = crud.get_all_books()
    text = f"📚 {books[int(book_id)-1].title}\n"
    text += f"👤 Автор: {books[int(book_id)-1].author}\n"
    text += f"🔸 Цена: {books[int(book_id)-1].price}\n"
    text += f"📂 Категория: {books[int(book_id)-1].category}\n"
    text += f"Выберите действие:"
    await state.update_data(book_id=book_id)
    await message.answer(text, reply_markup=await book_info_kb())

@dp.callback_query(F.data == 'description')
async def book_description(callback: CallbackQuery, state: FSMContext = None):
    book_id = await state.get_data()  
    book_id = book_id.get('book_id')  
    if not book_id:
        await callback.message.answer("Номер книги не может быть пустым. Введите номер книги:")
        return
    books = crud.get_all_books()
    text = f"{books[int(book_id)-1].description}\n"
    text += f"Выберите действие:"
    await callback.message.answer(text, reply_markup=await book_info_kb())

@dp.callback_query(F.data == 'buy_book')
async def buy_book(callback: CallbackQuery, state: FSMContext = None):
    book_id = await state.get_value('book_id')
    books = crud.get_all_books()
    book = books[int(book_id)-1]
    unique_id = uuid.uuid4().hex[:8]
    formatted_buy_text = BUY_TEXT.format(price=book.price)
    text = "💳 Оплата заказа\n\n"
    text = f"📚 {book.title}\n"
    text += f"👤 Автор: {book.author}\n"
    text += f"🔸 Цена: {book.price}\n"
    text += f"🆔 Комментарий: order_{unique_id}\n\n"
    text += formatted_buy_text
    await state.set_state(OrderAnswer.screenshot_id)
    await state.update_data(order_id=unique_id)
    await state.update_data(book_id=book_id)
    await callback.message.answer(text, reply_markup=await cancel_kb())

@dp.message(StateFilter(OrderAnswer.screenshot_id))
async def order_answer(message: Message, state: FSMContext = None):
    admin = crud.get_user(ADMIN_IDS[0])
    admin_chat = crud.get_user(ADMIN_IDS[0]).chat_id
    books = crud.get_all_books()
    book_id = await state.get_value('book_id')
    book = books[int(book_id)-1].uid
    book_name = books[int(book_id)-1].title
    screenshot_id = message.photo[0].file_id
    await state.update_data(screenshot_id=screenshot_id)
    order_id = await state.get_value('order_id')

    text = "✅ Скриншот оплаты получен!\n\n"
    text += f"📚 Книга: {book_name}\n"
    text += f"💰 Сумма: {books[int(book_id)-1].price}\n"
    text += f"🆔 Номер заказа: order_{order_id}\n"

    text1 = text
    text1 += f"📆 Дата создания: {datetime.datetime.now()}\n"
    text1 += f"Статус: Ожидание подтверждения\n"
    text1 += f"От кого: @{message.from_user.username} - {message.from_user.id}\n"

    crud.create_order(message.from_user.id, book, books[int(book_id)-1].price, screenshot_id, f"order_{order_id}",  "Ожидание подтверждения")
    await bot.send_photo(chat_id=admin_chat, photo=screenshot_id, caption=text1, reply_markup=await accept_order_kb())
    await message.answer(text, reply_markup=await on_start_kb())
    await state.clear()
    await state.set_state(AcceptOrder.order_id)
    await state.update_data(order_id=f"order_{order_id}")


#SHOW ORDERS
@dp.message(F.text.lower() == 'заказы')
async def show_orders(message: Message, state: FSMContext = None):
    orders = crud.get_orders_by_user(message.from_user.id)
    text = "Ваши заказы:\n"
    for order in orders:
        text += f"🆔 Номер заказа: {order.comment}\n"
        text += f"📚 Книга: {crud.get_book(order.book_uid).title}\n"
        text += f"💰 Сумма: {order.price}\n"
        text += f"📆 Дата создания: {order.created_at}\n"
        text += f"Статус: {order.status}\n"
        text += "\n"
    await message.answer(text, reply_markup=await on_start_kb())

#NEEDFIX
@dp.callback_query(F.data == 'help')
async def help_handler(callback: CallbackQuery, state: FSMContext = None):
    await callback.message.answer(HELP_TEXT, reply_markup=await on_start_kb())

#NEEDFIX
@dp.message(F.text.lower() == 'поддержка')
async def support_handler(message: Message, state: FSMContext = None):
    await message.answer('Напишите сообщение для поддержки', reply_markup=await on_start_kb())
    await state.set_state(Support.message_id)

@dp.message(StateFilter(Support.message_id))
async def support_answer(message: Message, state: FSMContext = None):
    admin_chat = crud.get_user(ADMIN_IDS[0]).chat_id
    uid = crud.create_question(message.text, message.from_user.id, message.from_user.username, message.chat.id).uid
    await bot.send_message(chat_id=admin_chat, text=f"[QUESTION]\n{uid}\n\nПользователь: @{message.from_user.username} - {message.from_user.id}\n\n{message.text}\n\nОтветьте на это сообщение, чтобы отправить ответ пользователю.")
    await state.clear()
