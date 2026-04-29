"""추상 Repository 인터페이스 (ABC)"""
from abc import ABC, abstractmethod
from typing import Optional
from app.models.user import UserInDB
from app.models.content import Content, ContentCreate


class BaseUserRepository(ABC):
    """사용자 데이터 접근 추상 인터페이스"""

    @abstractmethod
    def get_user_by_emp_id(self, emp_id: str) -> Optional[UserInDB]:
        ...

    @abstractmethod
    def list_all_users(self) -> list[UserInDB]:
        ...


class BaseContentRepository(ABC):
    """컨텐츠 데이터 접근 추상 인터페이스"""

    @abstractmethod
    def get_contents_by_emp_id(self, emp_id: str) -> list[Content]:
        ...

    @abstractmethod
    def get_all_contents(self) -> list[Content]:
        ...

    @abstractmethod
    def create_content(self, payload: ContentCreate, creator_id: str) -> Content:
        ...

    @abstractmethod
    def update_content(self, content_id: str, payload: dict) -> Optional[Content]:
        ...

    @abstractmethod
    def delete_content(self, content_id: str) -> bool:
        ...

    @abstractmethod
    def set_confirmation(self, content_id: str, emp_id: str, confirmed: bool, confirmed_text: str = "") -> bool:
        ...

    @abstractmethod
    def get_all_confirmations(self) -> list[dict]:
        ...

    @abstractmethod
    def get_confirmations_filtered(self, content_id: str | None = None, emp_id: str | None = None) -> list[dict]:
        ...
