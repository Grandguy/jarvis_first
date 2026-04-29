"""세션/인증 Pydantic 모델"""
from pydantic import BaseModel, field_validator
from typing import Literal
import re


class OTPRequestModel(BaseModel):
    """OTP 요청 모델"""
    emp_id: str

    @field_validator("emp_id")
    @classmethod
    def validate_emp_id(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9]{3,10}$", v):
            raise ValueError("유효하지 않은 사번 형식입니다.")
        return v.upper()


class OTPVerifyModel(BaseModel):
    """OTP 검증 모델"""
    emp_id: str
    otp: str

    @field_validator("emp_id")
    @classmethod
    def validate_emp_id(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9]{3,10}$", v):
            raise ValueError("유효하지 않은 사번 형식입니다.")
        return v.upper()

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        if not re.match(r"^\d{6}$", v):
            raise ValueError("OTP는 6자리 숫자여야 합니다.")
        return v


class ConfirmPayload(BaseModel):
    """열람 확인 토글 페이로드"""
    confirmed: bool
    answer_type: Literal[
        "yes_no", "text",
        "choice", "car_number", "plan_select", "education"
    ] = "yes_no"
    text: str = ""   # yes_no: "Yes"|"No", text: 자유입력
