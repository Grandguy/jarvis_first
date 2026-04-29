"""컨텐츠 CRUD 비즈니스 로직"""
from app.core.dependencies import get_content_repo
from app.models.content import Content, ContentCreate
from typing import Optional


def get_contents_for_user(emp_id: str) -> list[Content]:
    """특정 사용자의 컨텐츠 목록 조회"""
    repo = get_content_repo()
    return repo.get_contents_by_emp_id(emp_id)


def get_all_contents() -> list[Content]:
    """전체 컨텐츠 조회 (관리자용)"""
    repo = get_content_repo()
    return repo.get_all_contents()


def create_content(payload: ContentCreate, creator_id: str) -> Content:
    """컨텐츠 생성"""
    repo = get_content_repo()
    return repo.create_content(payload, creator_id)


def update_content(content_id: str, payload: dict) -> Optional[Content]:
    """컨텐츠 수정"""
    repo = get_content_repo()
    return repo.update_content(content_id, payload)


def delete_content(content_id: str) -> bool:
    """컨텐츠 삭제"""
    repo = get_content_repo()
    return repo.delete_content(content_id)


def set_confirmation(content_id: str, emp_id: str, confirmed: bool, confirmed_text: str = "") -> bool:
    """열람 확인 토글"""
    repo = get_content_repo()
    return repo.set_confirmation(content_id, emp_id, confirmed, confirmed_text)


def get_all_confirmations() -> list[dict]:
    """전체 확인 현황 조회 (관리자용)"""
    repo = get_content_repo()
    return repo.get_all_confirmations()


def get_confirmations_filtered(content_id: str | None = None, emp_id: str | None = None) -> list[dict]:
    """필터 조회 (관리자용)"""
    repo = get_content_repo()
    return repo.get_confirmations_filtered(content_id, emp_id)
