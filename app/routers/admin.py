"""관리자 라우터: CRUD + 사용자/확인현황 관리 + 파일 업로드"""
import shutil
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from app.core.dependencies import require_admin_user, get_user_repo, get_content_repo
from app.services import content_service
from app.models.content import ContentCreate, ContentUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 업로드 디렉토리
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/users")
async def list_users(_=Depends(require_admin_user)):
    """전체 사용자 목록"""
    user_repo = get_user_repo()
    users = user_repo.list_all_users()
    return [
        {"emp_id": u.emp_id, "name": u.name, "email": u.email, "is_admin": u.is_admin, "is_active": u.is_active}
        for u in users
    ]


@router.get("/contents")
async def list_all_contents(current_user=Depends(require_admin_user)):
    """전체 컨텐츠 목록"""
    contents = content_service.get_all_contents()
    return {"contents": [c.model_dump() for c in contents]}


@router.post("/contents")
async def create_content(
    payload: ContentCreate,
    current_user=Depends(require_admin_user)
):
    """컨텐츠 생성"""
    # 대상 사번 존재 여부 확인
    user_repo = get_user_repo()
    target_user = user_repo.get_user_by_emp_id(payload.target_emp_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="대상 사번이 존재하지 않습니다.")

    content = content_service.create_content(payload, current_user["sub"])
    return {"message": "컨텐츠가 생성되었습니다.", "content_id": content.content_id, "content": content.model_dump()}


@router.put("/contents/{content_id}")
async def update_content(
    content_id: str,
    payload: ContentUpdate,
    current_user=Depends(require_admin_user)
):
    """컨텐츠 수정"""
    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

    content = content_service.update_content(content_id, update_data)
    if not content:
        raise HTTPException(status_code=404, detail="컨텐츠를 찾을 수 없습니다.")
    return {"message": "수정되었습니다.", "content": content.model_dump()}


@router.delete("/contents/{content_id}")
async def delete_content(
    content_id: str,
    _=Depends(require_admin_user)
):
    """컨텐츠 삭제"""
    success = content_service.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="존재하지 않는 컨텐츠입니다.")
    return JSONResponse(status_code=200, content={"status": "deleted", "content_id": content_id})


@router.get("/confirmations")
async def get_confirmations(
    content_id: str | None = None,
    emp_id: str | None = None,
    _=Depends(require_admin_user)
):
    """확인 현황 필터 조회"""
    results = content_service.get_confirmations_filtered(content_id, emp_id)
    return results


# ── PATCH 2: 파일 업로드 (템플릿 4 교육자료 전용) ──

@router.post("/contents/{content_id}/upload")
async def upload_education_file(
    content_id: str,
    file: UploadFile = File(...),
    _=Depends(require_admin_user)
):
    """교육자료 파일 업로드"""
    # 허용 확장자 검사
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".pptx", ".docx", ".xlsx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"허용되지 않는 파일 형식: {ext}")

    # 파일명: content_id + 원본 확장자 (경로 추측 방지)
    save_name = f"{content_id}{ext}"
    save_path = UPLOAD_DIR / save_name

    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Excel에 file_path 업데이트
    content_repo = get_content_repo()
    content_repo.update_file_path(content_id, str(save_path))

    return {"status": "ok", "filename": save_name}
