"""의존성 주입 (세션 인증, 관리자 권한)"""
from fastapi import Cookie, HTTPException, status, Depends
from app.services.session_service import decode_session_token


async def require_authenticated_user(session_token: str = Cookie(None)):
    """인증된 사용자 세션 확인"""
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )
    try:
        payload = decode_session_token(session_token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었습니다."
        )


async def require_admin_user(user=Depends(require_authenticated_user)):
    """관리자 권한 확인"""
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    return user


def get_user_repo():
    """데이터 백엔드에 따른 Repository 선택"""
    from app.core.config import settings
    if settings.DATA_BACKEND == "db":
        # Phase 2: DBRepository
        raise NotImplementedError("DB 백엔드는 Phase 2에서 구현 예정입니다.")
    from app.repositories.excel_repository import ExcelUserRepository
    return ExcelUserRepository()


def get_content_repo():
    """데이터 백엔드에 따른 Content Repository 선택"""
    from app.core.config import settings
    if settings.DATA_BACKEND == "db":
        raise NotImplementedError("DB 백엔드는 Phase 2에서 구현 예정입니다.")
    from app.repositories.excel_repository import ExcelContentRepository
    return ExcelContentRepository()
