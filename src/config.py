import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    DATABASE_URL = (
        os.environ.get("DATABASE_URL") or "sqlite:///./database_management_1.db"
    )
