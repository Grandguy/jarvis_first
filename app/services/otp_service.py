"""OTP 생성, 캐시 저장, 메일 발송"""
import secrets
import ssl
import time
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

# 메모리 캐시 (Phase 1; Phase 2에서 Redis로 교체)
_otp_store: dict[str, dict] = {}
_attempt_store: dict[str, int] = {}


def generate_and_store_otp(emp_id: str) -> str:
    """OTP 6자리 생성 및 메모리 캐시에 저장"""
    otp = f"{secrets.randbelow(1_000_000):06d}"
    _otp_store[emp_id] = {"otp": otp, "created_at": time.time()}
    _attempt_store[emp_id] = 0
    return otp


async def send_otp_email(email: str, otp: str, name: str) -> None:
    """
    비동기 OTP 메일 발송 — HiWorks SMTP (SSL/465) 전용.
    FastAPI async 라우터에서 await으로 호출해야 한다.
    DEV_MODE에서는 콘솔 출력으로 대체.
    """
    subject = "[인증] 이메일 인증 코드 안내"
    body = (
        f"안녕하세요, {name}님.\n\n"
        f"인증 코드: {otp}\n\n"
        f"본 코드는 5분간 유효합니다.\n"
        f"본인이 요청하지 않은 경우 이 메일을 무시하세요."
    )

    if settings.DEV_MODE:
        print(f"\n{'='*50}")
        print(f"  [DEV MODE] OTP 이메일 발송 시뮬레이션")
        print(f"  수신자: {name} <{email}>")
        print(f"  인증 코드: {otp}")
        print(f"{'='*50}\n")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=int(settings.SMTP_PORT),
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,          # 포트 465 SSL 직접 연결
            timeout=15,
        )
        logger.info(f"OTP 메일 발송 완료 → {email}")

    except aiosmtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP 인증 실패: {e}")
        raise RuntimeError("이메일 인증 실패: 하이웍스 계정 정보를 확인하세요.")
    except aiosmtplib.SMTPConnectError as e:
        logger.error(f"SMTP 연결 실패: {e}")
        raise RuntimeError("메일 서버 연결 실패: smtps.hiworks.com:465 접근을 확인하세요.")
    except Exception as e:
        logger.error(f"메일 발송 오류: {e}")
        raise RuntimeError(f"메일 발송 중 오류 발생: {e}")


def verify_otp(emp_id: str, input_otp: str) -> tuple[bool, str]:
    """OTP 검증. 반환: (성공 여부, 실패 사유)"""
    record = _otp_store.get(emp_id)
    if not record:
        return False, "expired"

    if time.time() - record["created_at"] > settings.OTP_TTL:
        del _otp_store[emp_id]
        return False, "expired"

    attempts = _attempt_store.get(emp_id, 0)
    if attempts >= settings.OTP_MAX_ATTEMPTS:
        return False, "locked"

    if record["otp"] != input_otp:
        _attempt_store[emp_id] = attempts + 1
        return False, "mismatch"

    # 성공 시 캐시 정리
    del _otp_store[emp_id]
    del _attempt_store[emp_id]
    return True, "ok"
