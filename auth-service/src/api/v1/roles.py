import uuid
from fastapi import APIRouter, Depends, Header
from typing import Annotated

from depends import get_repository_user, get_admin
from schemas.entity import RoleCreate, UserRole
from services.user import BaseAuth
from services.admin import BaseAdmin

router = APIRouter()


@router.patch('/create/')
async def add_role(
        data: RoleCreate, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    """
    С помощью этого метода админ может добавить новую роль.

    :param data: (RoleCreate) Данные, необходимые для создания новой роли.
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return:
    Union[None | RoleCreate]: None, если пользователь не является админом,
    либо объект созданной роли. В противном случае выбрасывается исключение.
    """
    result = await manager_auth.get_info_from_access_token(user_agent)
    if result.get('is_admin'):
        role = await admin_manager.create_role(data)
        return role


@router.patch("/update/{role_id}/")
async def update_role(
        role_id: uuid.UUID,
        data: RoleCreate, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    """
    С помощью этого метода админ может редактировать имеющуюся роль.

    :param role_id: (UUID) id роли
    :param data: (RoleCreate) Данные, необходимые для редактирования роли.
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return:
    Union[None | RoleCreate]: None, если пользователь не является админом,
    либо объект отредактированной роли. В противном случае выбрасывается исключение.
    """
    result = await manager_auth.get_info_from_access_token(user_agent)
    if result.get('is_admin'):
        role = await admin_manager.update_role(role_id=role_id, new_data=data)
        return role


@router.post('/assign/')
async def assign_role(
        data: UserRole, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    """
    С помощью этого метода админ может присвоть пользователю роль.

    :param data: (UserRole) Данные, необходимые для присваивания роли: id пользователя и id роли
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return:
    Union[None | str]: None, если пользователь не является админом,
    либо строку 'role assigned'. В противном случае выбрасывается исключение.
    """
    result = await manager_auth.get_info_from_access_token(user_agent)
    if result.get('is_admin'):
        await admin_manager.assign_role(role_id=data.role_id, user_id=data.user_id)
        return 'role assigned'


@router.patch("/delete/{role_id}/")
async def delete_role(
        role_id: uuid.UUID, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    """
    С помощью этого метода админ может удалить роль.

    :param role_id: (UUID) id роли
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return:
    Union[None | str]: None, если пользователь не является админом,
    либо строку 'role deleted'. В противном случае выбрасывается исключение.
    """
    result = await manager_auth.get_info_from_access_token(user_agent)
    if result.get('is_admin'):
        await admin_manager.delete_role(role_id)
        return "role deleted"
