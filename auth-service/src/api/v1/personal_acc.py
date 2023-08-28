from services.user import UserManage

from fastapi import APIRouter, Depends, Header, Query
from typing import Annotated
from depends import get_user_manage
from schemas.entity import UserProfil, ChangeProfil, ChangePassword, HistoryUser, ChangeLevel
from core.config import PAGE_SIZE


router = APIRouter()


@router.get('/self_data/')
async def user_profile(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> UserProfil:
    '''
    Метод возвращает информацию о пользователе (профиль).

    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return: (UserProfil) Объект профиля. В противном случае выбрасывается исключение.
    '''
    user_profile: UserProfil = await user_manager.get_user_data(user_agent)
    return user_profile


@router.patch('/self_data/')
async def update_user_profile(
        self_data: ChangeProfil,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> UserProfil:
    '''
    Метод для редактирования профиля пользователя.

    :param self_data: (ChangeProfil) Данные, необходимые для изменения профиля.
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return: (UserProfil) Объект профиля. В противном случае выбрасывается исключение.
    '''
    user_profile: UserProfil = await user_manager.change_profile_user(user_agent, self_data)
    return user_profile


@router.post('/change_password/')
async def change_password(
        self_data: ChangePassword,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> str:
    '''
    Метод для изменения пароля пользователя.

    :param self_data: (ChangePassword) Данные о старом и новом пароле.
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return: (str) Строка "password changed". В противном случае выбрасывается исключение.
    '''
    await user_manager.change_password(user_agent, self_data)
    return "password changed"


@router.get('/user_history/')
async def user_history(
        page_number: Annotated[int, Query(description='Pagination page number', ge=1)] = 1,
        page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = PAGE_SIZE,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage),
) -> list[HistoryUser]:
    '''
    Метод возвращает историю входов пользователя на сайт, обновлений токенов и выходов.

    :param page_number: (int) Номер страницы
    :param page_size: (int) Количество записей на странице
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return:
    list[HistoryUser]: Список объектов модели HistoryUser. В противном случае выбрасывается исключение.
    '''
    user_history: list[HistoryUser] = await user_manager.get_history(user_agent, page_number, page_size)
    return user_history


@router.post('/change-level/')
async def change_level(
        self_data: ChangeLevel,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> str | None:
    '''
    Метод для изменения роли пользователя (повышения или понижения на 1 уровень).

    :param self_data: (ChangeLevel) Данные о том, повышать или понижать уровень роли
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :return:
    str: Строка "level raised" либо "level decreased".
    В противном случае выбрасывается исключение.
    '''
    await user_manager.change_level(user_agent, self_data.level_up)
    return "level raised" if self_data.level_up else "level decreased"
