"""FastAPI 앱 진입점 & 미들웨어 등록"""
from fastapi import FastAPI, Request, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.routers import auth, content, admin
from app.services.session_service import decode_session_token

# FastAPI 앱 생성
app = FastAPI(
    title="OTP 기반 컨텐츠 열람 시스템",
    version="1.0.0",
    docs_url="/docs",  # 개발환경에서만 활성화, 프로덕션에서는 None으로 변경
)

# 미들웨어
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 프로덕션에서는 도메인 제한
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿
templates = Jinja2Templates(directory="app/templates")

# 라우터 등록
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(admin.router)


@app.get("/", include_in_schema=False)
async def root():
    """진입점 → /app으로 리다이렉트"""
    return RedirectResponse(url="/app")


@app.get("/app", response_class=HTMLResponse, include_in_schema=False)
async def app_shell(request: Request, session_token: str = Cookie(None)):
    """SPA Shell 렌더링 — 인증 여부에 따라 레이어 분기"""
    is_authenticated = False
    is_admin = False
    emp_id = ""

    if session_token:
        try:
            payload = decode_session_token(session_token)
            is_authenticated = True
            is_admin = payload.get("is_admin", False)
            emp_id = payload.get("sub", "")
        except Exception:
            # 토큰 만료/변조 시 미인증 상태로 처리
            pass

    return templates.TemplateResponse(
        "shell.html",
        {
            "request": request,
            "is_authenticated": is_authenticated,
            "is_admin": is_admin,
            "emp_id": emp_id,
        }
    )
