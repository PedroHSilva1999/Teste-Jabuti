from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.cache import cache_client
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def list_users(self, limit: int, offset: int) -> UserListResponse:
        cache_key = f"usuarios:list:{limit}:{offset}"
        cached = cache_client.get_json(cache_key)
        if cached is not None:
            return UserListResponse.model_validate(cached)

        users, total = self.repository.list(limit=limit, offset=offset)
        response = UserListResponse(
            items=[UserResponse.model_validate(user) for user in users],
            total=total,
            limit=limit,
            offset=offset,
        )
        cache_client.set_json(cache_key, jsonable_encoder(response))
        return response

    def get_user(self, user_id: UUID) -> UserResponse:
        cache_key = f"usuarios:detail:{user_id}"
        cached = cache_client.get_json(cache_key)
        if cached is not None:
            return UserResponse.model_validate(cached)

        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

        response = UserResponse.model_validate(user)
        cache_client.set_json(cache_key, jsonable_encoder(response))
        return response

    def create_user(self, payload: UserCreate) -> UserResponse:
        existing = self.repository.get_by_email(payload.email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

        user = self.repository.create(payload)
        self._invalidate_user_caches(user.id)
        return UserResponse.model_validate(user)

    def update_user(self, user_id: UUID, payload: UserUpdate) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

        existing = self.repository.get_by_email(payload.email)
        if existing is not None and existing.id != user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

        updated_user = self.repository.update(user, payload)
        self._invalidate_user_caches(user_id)
        return UserResponse.model_validate(updated_user)

    def delete_user(self, user_id: UUID) -> None:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

        self.repository.delete(user)
        self._invalidate_user_caches(user_id)

    def _invalidate_user_caches(self, user_id: UUID) -> None:
        cache_client.delete_pattern("usuarios:list:*")
        cache_client.delete_keys([f"usuarios:detail:{user_id}"])
