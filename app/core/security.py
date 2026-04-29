"""세션 토큰 생성/검증, 보안 유틸리티"""
import hashlib
import secrets


def generate_random_token(length: int = 32) -> str:
    """보안 난수 토큰 생성"""
    return secrets.token_urlsafe(length)


def hash_path(path: str) -> str:
    """경로 해싱 (경로 은닉용)"""
    return hashlib.sha256(path.encode()).hexdigest()[:16]
