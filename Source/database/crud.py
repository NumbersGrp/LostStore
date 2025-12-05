from database.models import Books, User, Setting, Orders, Questions
from database.database import create_session

session = create_session()

def ensure_session_ready():
    try:
        session.rollback()
    except Exception:
        pass

class UserManager:
    def __init__(self):
        self.create_default_admins()

    def create_default_admins(self):
        try:
            self.create_user("twelvefacedjanu", 7978367962, role="admin")
            #self.create_user("AlinaVinshu", 724595286, role="admin")
            pass
        except Exception as e:
            session.rollback()
            raise e

    def create_user(self, tusername: str, tid: int, role: str = "user", chat_id: int = 0):
        try:
            ensure_session_ready()
            if self.get_user(tid): return self.get_user(tid)
            user = User(tusername=tusername, tid=tid, role=role, chat_id=chat_id)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        
    def get_user(self, tid: int):
        try:
            ensure_session_ready()
            user = session.query(User).filter(User.tid == tid).first()
            return user
        except Exception as e:
            session.rollback()
            raise e

    def get_all_users(self):
        try:
            ensure_session_ready()
            users = session.query(User).all()
            return users
        except Exception as e:
            session.rollback()
            raise e
        
    def get_all_admins(self):
        try:
            ensure_session_ready()
            admins = session.query(User).filter(User.role == "admin").all()
            return admins
        except Exception as e:
            session.rollback()
            raise e


class BookManager:
    def __init__(self):
        pass

    def get_all_books(self):
        try:
            ensure_session_ready()
            books = session.query(Books).all()
            return books
        except Exception as e:
            session.rollback()
            raise e
    
    def get_book(self, uid: str):
        try:
            ensure_session_ready()
            book = session.query(Books).filter(Books.uid == uid).first()
            return book
        except Exception as e:
            session.rollback()
            raise e

    def create_book(self, title: str = '', image_id: int = 0, author: str = '', description: str = '', price: int = 0, category: str = '', file_ids: list = [], chat_id: int = 0):
        try:
            ensure_session_ready()
            book = Books(title=title, image_id=image_id, author=author, description=description, price=price, category=category, file_ids=file_ids, chat_id=chat_id)
            session.add(book)
            session.commit()
            return book
        except Exception as e:
            session.rollback()
            raise e

    def delete_book(self, title: str):
        try:
            ensure_session_ready()
            book = session.query(Books).filter(Books.title == title).first()
            session.delete(book)
            session.commit()
            return book
        except Exception as e:
            session.rollback()
            raise e

class OrderManager:
    def __init__(self):
        pass

    def get_all_orders(self):
        try:
            ensure_session_ready()
            orders = session.query(Orders).all()
            return orders
        except Exception as e:
            session.rollback()
            raise e
        
    def get_order(self, comment: str):
        try:
            ensure_session_ready()
            order = session.query(Orders).filter(Orders.comment == comment).first()
            return order
        except Exception as e:
            session.rollback()
            raise e
        
    def get_orders_by_user(self, user_tid: str):
        try:
            ensure_session_ready()
            orders = session.query(Orders).filter(Orders.user_tid == user_tid).all()
            return orders
        except Exception as e:
            session.rollback()
            raise e
    
    def create_order(self, user_tid: str, book_uid: str, price: int, screenshot: str, comment: str, status: str):
        try:
            ensure_session_ready()
            order = Orders(user_tid=user_tid, book_uid=book_uid, price=price, screenshot=screenshot, comment=comment, status=status)
            session.add(order)
            session.commit()
            return order
        except Exception as e:
            session.rollback()
            raise e
        
    def delete_order(self, uid: str):
        try:
            ensure_session_ready()
            order = session.query(Orders).filter(Orders.uid == uid).first()
            session.delete(order)
            session.commit()
            return order
        except Exception as e:
            session.rollback()
            raise e
    
    def update_order(self, comment: str, status: str):
        try:
            ensure_session_ready()
            order = session.query(Orders).filter(Orders.comment == comment).first()
            order.status = status
            session.commit()
            return order
        except Exception as e:
            session.rollback()
            raise e
        
    
# class Questions(Base):
#     __tablename__ = 'questions'

#     uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
#     text = Column(String, nullable=False)
#     user_uid = Column(String, nullable=False)
#     tusername = Column(String, nullable=False)
#     tid = Column(BigInteger, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
class QuestionManager:
    def __init__(self):
        pass

    def get_questions(self):
        try:
            ensure_session_ready()
            questions = session.query(Questions).all()
            return questions
        except Exception as e:
            session.rollback()
            raise e
        
    def get_question(self, uid: str):
        try:
            ensure_session_ready()
            question = session.query(Questions).filter(Questions.uid == uid).first()
            return question
        except Exception as e:
            session.rollback()
            raise e
        
    def create_question(self, text: str, user_uid: str, tusername: str, chat_id: int):
        try:
            ensure_session_ready()
            question = Questions(text=text, user_uid=user_uid, tusername=tusername, chat_id=chat_id)
            session.add(question)
            session.commit()
            return question
        except Exception as e:
            session.rollback()
            raise e

    def delete_question(self, uid: str):
        try:
            ensure_session_ready()
            question = session.query(Questions).filter(Questions.uid == uid).first()
            session.delete(question)
            session.commit()
            return question
        except Exception as e:
            session.rollback()
            raise e
        

class SettingsManager:
    def __init__(self):
        pass

    def get_setting(self, key: str):
        try:
            ensure_session_ready()
            s = session.query(Setting).filter(Setting.key == key).first()
            return s.value if s else None
        except Exception as e:
            session.rollback()
            raise e

    def set_setting(self, key: str, value: str):
        try:
            ensure_session_ready()
            s = session.query(Setting).filter(Setting.key == key).first()
            if s:
                s.value = value
            else:
                s = Setting(key=key, value=value)
                session.add(s)
            session.commit()
            return s
        except Exception as e:
            session.rollback()
            raise e


class Crud(UserManager, BookManager, OrderManager, QuestionManager, SettingsManager):
    def __init__(self):
        super().__init__()
