from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status
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
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Quantidade máxima de usuários retornados.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Deslocamento para paginação (quantidade a pular).",
    ),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """Lista usuários com paginação."""
    return service.list_users(limit=limit, offset=offset)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
    description="Recupera um usuário pelo `user_id`.",
)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> UserResponse:
    """Obtém um usuário pelo seu identificador."""
    return service.get_user(user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description="Cria um novo usuário.",
    responses={
        status.HTTP_201_CREATED: {"description": "Usuário criado."},
        status.HTTP_409_CONFLICT: {"description": "Email ja cadastrado."},
    },
)
def create_user(
    payload: UserCreate = Body(..., description="Dados do usuário a ser criado."),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Cria um novo usuário."""
    return service.create_user(payload)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuário",
    description="Atualiza os dados de um usuário existente.",
    responses={
        status.HTTP_200_OK: {"description": "Usuário atualizado."},
        status.HTTP_404_NOT_FOUND: {"description": "Usuario nao encontrado."},
        status.HTTP_409_CONFLICT: {"description": "Email ja cadastrado."},
    },
)
def update_user(
    user_id: UUID = Path(..., description="ID do usuário a atualizar."),
    payload: UserUpdate = Body(..., description="Dados atualizados do usuário."),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Atualiza um usuário pelo seu identificador."""
    return service.update_user(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir usuário",
    description="Remove um usuário pelo `user_id`.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Usuário excluído."},
        status.HTTP_404_NOT_FOUND: {"description": "Usuario nao encontrado."},
    },
)
def delete_user(
    user_id: UUID = Path(..., description="ID do usuário a excluir."),
    service: UserService = Depends(get_user_service),
) -> Response:
    """Exclui um usuário pelo seu identificador."""
    service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
