from aiogram.fsm.state import StatesGroup, State

class Effect(StatesGroup):
    message_id = State()

class StartPdf(StatesGroup):
    waiting_for_document = State()
    waiting_for_text = State()

# uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
# title = Column(String, nullable=False)
# image_id = Column(String)
# author = Column(String, nullable=False)
# description = Column(String, nullable=False)
# price = Column(Integer, nullable=False)
# category = Column(String, nullable=False)
# file_ids = Column(ARRAY(String), nullable=False)
# chat_id = Column(BigInteger, nullable=False)
# created_at = Column(DateTime(timezone=True), server_default=func.now())
# updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AddNewBook(StatesGroup):
    title = State()
    author = State()
    description = State()
    price = State()
    category = State()
    image_id = State()
    file_ids = State()

class ChooseBook(StatesGroup):
    book_id = State()

class OrderAnswer(StatesGroup):
    screenshot_id = State()
    order_id = State()
    book_id = State()

class DeleteBook(StatesGroup):
    title = State()

class AcceptOrder(StatesGroup):
    order_id = State()