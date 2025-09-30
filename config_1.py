import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL_1", "sqlite:///database_management_1.db")
SMTP_SERVER = os.getenv("SMTP_SERVER_1") or os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT_1") or os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL_1") or os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD_1") or os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL_1") or os.getenv("RECIPIENT_EMAIL")
RECIPIENT_EMAIL_2 = os.getenv("RECIPIENT_EMAIL_2_1") or os.getenv("RECIPIENT_EMAIL_2")
