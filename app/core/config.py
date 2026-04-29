"""환경 변수 설정"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 보안
    SECRET_KEY: str = "change-me-in-production"

    # 데이터 백엔드
    DATA_BACKEND: str = "excel"  # excel | db
    EXCEL_PATH: str = "data/master.xlsx"

    # SMTP (OTP 메일 발송)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # 개발 모드 (이메일 발송 대신 콘솔 출력)
    DEV_MODE: bool = True

    # JWT
    TOKEN_EXPIRE_HOURS: int = 8

    # OTP
    OTP_TTL: int = 300  # 5분
    OTP_MAX_ATTEMPTS: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
