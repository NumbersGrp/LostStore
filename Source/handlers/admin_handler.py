from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from core.bot import dp, bot
from database.crud import Crud
from keyboards.admin_keyboards import *
from aiogram import F
from aiogram.filters import BaseFilter
from states.effect import AddNewBook, DeleteBook, AcceptOrder
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.media_group import MediaGroupBuilder
import asyncio


crud = Crud()
ADMIN_IDS = crud.get_all_admins()
ADMIN_IDS = [admin.tid for admin in ADMIN_IDS]
media = []

WELCOME_TEXT = ''

with open("Source/content/welcome_text.txt", "r") as f:
    WELCOME_TEXT = f.read()

class IsAdmin(BaseFilter):
        async def __call__(self, message: Message) -> bool:
            return message.from_user.id in ADMIN_IDS
        
@dp.message(Command('admin'), IsAdmin())
async def admin_handler(message: Message, state: FSMContext = None):
    await message.answer("Добро пожаловать, в админ панель!", reply_markup=await on_admin_start_kb())

@dp.callback_query(F.data == 'admin_start', IsAdmin())
async def admin_start(message: Message, state: FSMContext = None):
    await admin_handler(message, state)

@dp.message(F.text.lower() == 'управление книгами', IsAdmin())
async def manage_books(message: Message, state: FSMContext = None):
    books = crud.get_all_books()
    text = "📚Список книг:\n"
    if books == None:
        await message.answer("Список книг пуст.", reply_markup=await manage_books_kb())
    for book in books:
        text += f"{book.title} - {book.author}\n"
        text += f"Цена книги: {book.price}\n"
        text += f"Категория: {book.category}\n"
        text += f"Дата создания: {book.created_at}\n"
    await message.answer(text, reply_markup=await manage_books_kb())

#ADD NEW BOOK SEQUENCE
@dp.callback_query(F.data == 'add_book', IsAdmin())
async def add_book(message: Message, state: FSMContext = None):
    await message.answer("Введите название книги:")
    await state.set_state(AddNewBook.title)

@dp.message(StateFilter(AddNewBook.title))
async def add_book_set_title(message: Message, state: FSMContext = None):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название книги не может быть пустым. Введите название книги:")
        return
    await state.update_data(title=title)
    await state.set_state(AddNewBook.author)
    await message.answer("Введите автора книги:")

@dp.message(StateFilter(AddNewBook.author))
async def add_book_set_author(message: Message, state: FSMContext = None):
    author = (message.text or "").strip()
    if not author:
        await message.answer("Автор книги не может быть пустым. Введите автора книги:")
        return
    await state.update_data(author=author)
    await state.set_state(AddNewBook.description)
    await message.answer("Введите описание книги:")

@dp.message(StateFilter(AddNewBook.description))
async def add_book_set_description(message: Message, state: FSMContext = None):
    description = (message.text or "").strip()
    if not description:
        await message.answer("Описание книги не может быть пустым. Введите описание книги:")
        return
    await state.update_data(description=description)
    await state.set_state(AddNewBook.description_image_ids)
    await message.answer("Отправите изображения описания книги или напишите 'пропустить' и продолжите добавление книги.")

@dp.message(StateFilter(AddNewBook.description_image_ids))
async def add_book_set_description_image_ids(message: Message, state: FSMContext = None):
    global media
    try:
        if message.text.lower() == 'пропустить':
            await state.update_data(description_image_ids=media)
            await state.set_state(AddNewBook.price)
            await message.answer("Введите цену книги:")
            media = []
            return
    except:
        pass
    if not message.photo:
        await message.answer("Изображения описания книги не может быть пустой. Отправите изображения описания книги:")
        return
    media.append(message.photo[0].file_id)

@dp.message(StateFilter(AddNewBook.price))
async def add_book_set_price(message: Message, state: FSMContext = None):
    price = (message.text or "").strip()
    if not price:
        await message.answer("Цена книги не может быть пустой. Введите цену книги:")
        return
    await state.update_data(price=price)
    await state.set_state(AddNewBook.category)
    await message.answer("Введите категорию книги:")

@dp.message(StateFilter(AddNewBook.category))
async def add_book_set_category(message: Message, state: FSMContext = None):
    category = (message.text or "").strip()
    if not category:
        await message.answer("Категория книги не может быть пустой. Введите категорию книги:")
        return
    await state.update_data(category=category)
    await state.set_state(AddNewBook.image_id)
    await message.answer("Отправьте или перешлите изображение книги. Его ID будет сохранён.")

@dp.message(StateFilter(AddNewBook.image_id))
async def add_book_set_image_id(message: Message, state: FSMContext = None):
    image_id = message.photo[0].file_id
    if not image_id:
        await message.answer("ID изображения книги не может быть пустой. Введите ID изображения книги:")
        return
    await state.update_data(image_id=image_id)
    await state.set_state(AddNewBook.file_ids)
    await message.answer("Отправьте или перешлите PDF-файл книги. Его ID будет сохранён.")

@dp.message(StateFilter(AddNewBook.file_ids))
async def add_book_set_file_ids(message: Message, state: FSMContext = None):
    global media
    try:
        if message.text.lower() == 'пропустить':
            await state.update_data(file_ids=media)
            data = await state.get_data()
            crud.create_book(data['title'], data['image_id'], data['author'], data['description'], data['description_image_ids'], data['price'], data['category'], data['file_ids'], message.chat.id)
            await message.answer("Книга успешно добавлена.", reply_markup=await on_admin_start_kb())
            await state.clear()
            return
    except:
        pass
    file_ids = message.document.file_id
    if not file_ids:
        await message.answer("ID PDF-файла книги не может быть пустой. Введите ID PDF-файла книги:")
        return
    media.append(file_ids)

#DELETE BOOK SEQUENCE
@dp.callback_query(F.data == 'delete_book', IsAdmin())
async def delete_book(message: Message, state: FSMContext = None):
    await message.answer("Введите название книги, которую хотите удалить:", reply_markup=await on_admin_start_kb())
    await state.set_state(DeleteBook.title)

@dp.message(StateFilter(DeleteBook.title))
async def delete_book(message: Message, state: FSMContext = None):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название книги не может быть пустым. Введите название книги:")
        return
    crud.delete_book(title)
    await message.answer("Книга успешно удалена.", reply_markup=await on_admin_start_kb())
    await state.clear()

#ORDER ACCEPT
@dp.callback_query(F.data == 'accept_order', IsAdmin())
async def accept_order(callback: CallbackQuery, state: FSMContext = None):
    order_id = await state.get_value('order_id')
    print(order_id)
    crud.update_order(order_id, "Принят")
    order = crud.get_order(order_id)
    user_chat = crud.get_user(order.user_tid).chat_id
    files_id = crud.get_book(order.book_uid).file_ids    
    media_group = MediaGroupBuilder()
    for i in files_id:
        media_group.add_document(i)
    await bot.send_message(chat_id=user_chat, text=f"Ваш заказ принят. Номер заказа: {order_id}")
    await bot.send_media_group(chat_id=user_chat, media=media_group.build())
    await callback.message.answer("Заказ успешно принят.", reply_markup=await on_admin_start_kb())
    await state.clear()

#ORDER DECLINE
@dp.callback_query(F.data == 'decline_order', IsAdmin())
async def decline_order(callback: CallbackQuery, state: FSMContext = None):
    order_id = await state.get_value('order_id')
    order = crud.get_order(order_id)
    crud.update_order(order_id, "Отклонён")
    user_chat = crud.get_user(order.user_tid).chat_id
    await bot.send_message(chat_id=user_chat, text=f"Ваш заказ принят. Номер заказа: {order_id}")
    await callback.message.answer("Заказ успешно отклонён.", reply_markup=await on_admin_start_kb())
    await state.clear()

#LIST OF ORDERS
@dp.message(F.text.lower() == 'список заказов', IsAdmin())
async def show_orders(message: Message, state: FSMContext = None):
    orders = crud.get_all_orders()
    text = "Список заказов:\n"
    for order in orders:
        text += f"👤 Пользователь: @{crud.get_user(order.user_tid).tusername} - {order.user_tid}\n"
        text += f"🆔 Номер заказа: {order.comment}\n"
        text += f"📚 Книга: {crud.get_book(order.book_uid).title}\n"
        text += f"💰 Сумма: {order.price}\n"
        text += f"📆 Дата создания: {order.created_at}\n"
        text += f"Статус: {order.status}\n"
        text += "\n"
    await message.answer(text, reply_markup=await on_admin_start_kb())

@dp.message(F.reply_to_message != None)
async def reply_to_question(message: Message, state: FSMContext = None):
    print('1')
    if message.reply_to_message:
        print('2')
        uid = message.reply_to_message.text.split('\n')[1]
        question = crud.get_question(uid)
        text = "Ответ на вопрос:\n"
        text += message.text
        await bot.send_message(chat_id=question.chat_id, text=text)
        print('3')
    print('4')