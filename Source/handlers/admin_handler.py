from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from core.bot import dp, bot
from database.crud import Crud
from keyboards.admin_keyboards import *
from aiogram import F
from aiogram.filters import BaseFilter
from states.effect import AddNewBook, DeleteBook
from states.lesson_manager import AddNewLesson
from states.lesson_manager import AddLessonContent
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import asyncio


crud = Crud()
ADMIN_IDS = crud.get_all_admins()
ADMIN_IDS = [admin.tid for admin in ADMIN_IDS]

WELCOME_TEXT = ''

with open("Source/content/welcome_text.txt", "r") as f:
    WELCOME_TEXT = f.read()

class IsAdmin(BaseFilter):
        async def __call__(self, message: Message) -> bool:
            return message.from_user.id in ADMIN_IDS
        
@dp.message(Command('admin'), IsAdmin())
async def admin_handler(message: Message, state: FSMContext = None):
    sent_message = await message.answer("Добро пожаловать, в админ панель!", reply_markup=await on_admin_start_kb())

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
    await state.set_state(AddNewBook.price)
    await message.answer("Введите цену книги:")

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
    file_ids = message.document.file_id
    if not file_ids:
        await message.answer("ID PDF-файла книги не может быть пустой. Введите ID PDF-файла книги:")
        return
    await state.update_data(file_ids=file_ids)
    data = await state.get_data()
    crud.create_book(data['title'],data['image_id'], data['author'], data['description'], data['price'], data['category'], [data['file_ids']], message.chat.id)
    await message.answer("Книга успешно добавлена.", reply_markup=await on_admin_start_kb())
    await state.clear()

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
    await bot.send_message(chat_id=user_chat, text=f"Ваш заказ принят. Номер заказа: {order_id}")
    await bot.send_media_group(chat_id=user_chat, media=files_id)
    await callback.message.answer("Заказ успешно принят.", reply_markup=await on_admin_start_kb())
    await state.clear()

#ORDER DECLINE
@dp.callback_query(F.data == 'decline_order', IsAdmin())
async def decline_order(callback: CallbackQuery, state: FSMContext = None):
    order_id = await state.get_value('order_id')
    crud.update_order(order_id, "Отклонён")
    order = crud.get_order(order_id)
    await bot.send_message(chat_id=order.user_id, text=f"Ваш заказ отклонён. Номер заказа: {order_id}")
    await callback.message.answer("Заказ успешно отклонён.", reply_markup=await on_admin_start_kb())
    await state.clear()