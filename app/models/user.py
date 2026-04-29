"""사용자 Pydantic 모델"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    """사용자 기본 모델"""
    emp_id: str
    name: str
    email: EmailStr


class UserInDB(User):
    """DB/Excel 저장용 사용자 모델"""
    is_admin: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
