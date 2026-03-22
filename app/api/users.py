from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)


@router.get("", response_model=UserListResponse)
def list_users(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    return service.list_users(limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.get_user(user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.create_user(payload)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return service.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> Response:
    service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
