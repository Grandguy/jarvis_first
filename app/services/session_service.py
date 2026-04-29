"""JWT 기반 세션 발급/검증"""
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

ALGORITHM = "HS256"


def create_session_token(emp_id: str, is_admin: bool) -> str:
    """JWT 세션 토큰 생성"""
    payload = {
        "sub": emp_id,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_session_token(token: str) -> dict:
    """JWT 세션 토큰 검증 및 디코딩.
    만료/변조 시 jwt.ExpiredSignatureError / jwt.InvalidTokenError 발생
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
