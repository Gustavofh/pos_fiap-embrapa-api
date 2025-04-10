# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID")
    BIGQUERY_PROJECT_ID: str = os.getenv("BIGQUERY_PROJECT_ID")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str  = "gustavofh94@gmail.com"
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")


settings = Settings()
