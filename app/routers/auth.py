"""인증 라우터: OTP 요청/검증"""
from fastapi import APIRouter, HTTPException, status, Response
from app.models.session import OTPRequestModel, OTPVerifyModel
from app.services import otp_service
from app.services.session_service import create_session_token
from app.core.dependencies import get_user_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/step1")
async def request_otp(payload: OTPRequestModel):
    """사번 입력 → OTP 생성 및 이메일 발송"""
    user_repo = get_user_repo()
    user = user_repo.get_user_by_emp_id(payload.emp_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="등록되지 않은 사번입니다."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다. 관리자에게 문의하세요."
        )

    # OTP 생성 및 저장
    otp = otp_service.generate_and_store_otp(payload.emp_id)

    # 이메일 발송 (DEV_MODE에서는 콘솔 출력)
    await otp_service.send_otp_email(user.email, otp, user.name)

    return {"message": "OTP가 발송되었습니다.", "email_hint": f"{user.email[:3]}***"}


@router.post("/step2")
async def verify_otp(payload: OTPVerifyModel, response: Response):
    """OTP 검증 → JWT 세션 토큰 발급"""
    user_repo = get_user_repo()
    user = user_repo.get_user_by_emp_id(payload.emp_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="등록되지 않은 사번입니다."
        )

    success, reason = otp_service.verify_otp(payload.emp_id, payload.otp)

    if not success:
        if reason == "expired":
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="OTP가 만료되었습니다. 다시 요청해주세요."
            )
        elif reason == "locked":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="인증 시도 횟수를 초과했습니다. 새 OTP를 요청해주세요."
            )
        else:  # mismatch
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 코드가 일치하지 않습니다."
            )

    # JWT 세션 토큰 발급
    token = create_session_token(user.emp_id, user.is_admin)

    # HttpOnly Cookie로 세팅
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,  # 개발환경: False, 프로덕션: True
        samesite="strict",
        max_age=60 * 60 * 8,  # 8시간
        path="/",
    )

    return {
        "message": "인증 성공",
        "user": {
            "emp_id": user.emp_id,
            "name": user.name,
            "is_admin": user.is_admin,
        }
    }


@router.post("/logout")
async def logout(response: Response):
    """로그아웃 — 세션 쿠키 삭제"""
    response.delete_cookie(key="session_token", path="/")
    return {"message": "로그아웃되었습니다."}
