"""컨텐츠 Pydantic 모델"""
from pydantic import BaseModel
from typing import Optional, Literal, Any
from datetime import datetime


class ContentCreate(BaseModel):
    """컨텐츠 생성 요청"""
    title: str
    target_emp_id: str
    body_1: str
    body_2: Optional[str] = None
    body_3: Optional[str] = None
    answer_type: Literal[
        "yes_no", "text",
        "choice", "car_number", "plan_select", "education"
    ] = "yes_no"
    template_config: dict[str, Any] = {}  # 템플릿별 추가 설정 (JSON으로 직렬화 저장)


class ContentUpdate(BaseModel):
    """컨텐츠 수정 요청"""
    title: Optional[str] = None
    body_1: Optional[str] = None
    body_2: Optional[str] = None
    body_3: Optional[str] = None


class Content(BaseModel):
    """컨텐츠 응답 모델"""
    content_id: str
    title: str
    target_emp_id: str
    body_1: str
    body_2: Optional[str] = None
    body_3: Optional[str] = None
    answer_type: str = "yes_no"
    template_config: dict[str, Any] = {}  # 템플릿별 추가 설정
    created_by: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    file_path: Optional[str] = None       # 템플릿 4 전용
    is_confirmed: bool = False
    confirmed_at: Optional[datetime] = None
    confirmed_text: str = ""
