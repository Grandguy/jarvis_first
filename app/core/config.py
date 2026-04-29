"""환경 변수 설정"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 보안
    SECRET_KEY: str = "change-me-in-production"

    # 데이터 백엔드
    DATA_BACKEND: str = "excel"  # excel | db
    EXCEL_PATH: str = "data/master.xlsx"

    # SMTP 설정 (이곳에 실제 정보를 직접 입력)
    SMTP_HOST: str = "smtps.hiworks.com" # 또는 smtp.gmail.com
    SMTP_PORT: int = 465
    SMTP_USER: str = "real.jung@kbs.co.kr"
    SMTP_PASSWORD: str = "tkakrnl333"
    SMTP_FROM: str = "real.jung@kbs.co.kr"
    # 중요: 운영 환경에서는 False로 설정해야 실제 메일이 발송됨
    DEV_MODE: bool = False 

    # JWT
    TOKEN_EXPIRE_HOURS: int = 8

    # OTP
    OTP_TTL: int = 300  # 5분
    OTP_MAX_ATTEMPTS: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
