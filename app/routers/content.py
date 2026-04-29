"""컨텐츠 라우터: 사용자 열람 및 확인"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.dependencies import require_authenticated_user
from app.services import content_service
from app.models.session import ConfirmPayload

router = APIRouter(tags=["content"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/fragment/auth", response_class=HTMLResponse)
async def get_auth_fragment(request: Request):
    """인증 레이어 Fragment"""
    return templates.TemplateResponse(
        "fragments/auth_layer.html",
        {"request": request}
    )


@router.get("/fragment/content", response_class=HTMLResponse)
async def get_content_fragment(
    request: Request,
    current_user=Depends(require_authenticated_user)
):
    """컨텐츠 레이어 Fragment (인증 필수)"""
    contents = content_service.get_contents_for_user(current_user["sub"])
    return templates.TemplateResponse(
        "fragments/content_layer.html",
        {"request": request, "contents": contents, "user": current_user}
    )


@router.get("/fragment/admin", response_class=HTMLResponse)
async def get_admin_fragment(
    request: Request,
    current_user=Depends(require_authenticated_user)
):
    """관리자 레이어 Fragment (관리자 인증 필수)"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return templates.TemplateResponse(
        "fragments/admin_layer.html",
        {"request": request, "user": current_user}
    )


@router.patch("/api/content/{content_id}/confirm")
async def confirm_content(
    content_id: str,
    payload: ConfirmPayload,
    current_user=Depends(require_authenticated_user)
):
    """열람 확인 토글"""
    success = content_service.set_confirmation(
        content_id=content_id,
        emp_id=current_user["sub"],
        confirmed=payload.confirmed,
        confirmed_text=payload.text,
    )
    if not success:
        raise HTTPException(status_code=404, detail="컨텐츠를 찾을 수 없습니다.")
    return {"status": "ok"}


@router.get("/api/content")
async def get_my_contents(current_user=Depends(require_authenticated_user)):
    """내 컨텐츠 JSON API"""
    contents = content_service.get_contents_for_user(current_user["sub"])
    return {"contents": [c.model_dump() for c in contents]}
