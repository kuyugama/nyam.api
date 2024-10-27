from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from src.models import User
from celery_app import celery


@lru_cache(maxsize=-1)
def init_db():
    engine = create_engine(settings.postgresql.celery_url)
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    return init_db()()


@celery.task()
def new_login(user_id: int, address: str):
    with get_session() as session:
        user = session.get(User, user_id)

        assert isinstance(user, User), f"Non-User instance returned by sqlalchemy - {user!r}[{user}]"

        print(f"New login to user with ID {user_id} - {user.nickname} from address {address}")
        print(f"Tokens count {len(user.tokens)}")
