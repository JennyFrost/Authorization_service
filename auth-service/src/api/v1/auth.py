from fastapi import APIRouter, Depends, Header, Request
from typing import Annotated

from depends import get_repository_user
from schemas.entity import UserCreate, UserLogin
from services.user import BaseAuth

router = APIRouter()


@router.post('/login/')
async def login(
        data: UserLogin, user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseAuth = Depends(get_repository_user)
):
    """
     Авторизация и аутентификация пользователя и создание токенов.

    :param data: (UserLogin) Данные, необходимые для аутентификации пользователя (логин и пароль).
    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    """
    await user_manager.log_in(data, user_agent)


@router.post('/sign_up/')
async def sign_up(data: UserCreate, user_manager: BaseAuth = Depends(get_repository_user)):
    """
    Регистрирует нового пользователя.

    :param data: (UserCreate) Данные, необходимые для создания нового пользователя.
    :return:
    None: Если регистрация прошла успешно. В противном случае выбрасывется исключение.
    """
    await user_manager.sign_up(data)


@router.get('/user_info/')
async def user_info(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseAuth = Depends(get_repository_user)
):
    """
    Получает информацию из access token и проверяет его безопасность.

    :param user_agent: (str) Заголовок User-Agent, для сравнения с данными из access token.
    :return:
    dict: Словарь с информацией из access token. В противном случае выбрасывается исключение.
    """
    return await user_manager.get_info_from_access_token(user_agent)


@router.post('/refresh/')
async def refresh(
        request: Request, user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseAuth = Depends(get_repository_user),
):
    """
    Обновляет access token и возвращает его.

    :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
    :param request: (Request) Объект запроса, содержащий cookies с refresh token и access token.
    :return:
    str: Обновленный access token, если все проверки прошли успешно.
    В противном случае выбрасывается исключение.
    """
    result = await user_manager.refresh_token(user_agent, request)
    return result


@router.get('/logout/')
async def logout(
        request: Request, user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseAuth = Depends(get_repository_user)):
    """
    Осуществляет выход пользователя из системы (logout).

    :param request: (Request) Объект запроса, содержащий cookies с данными о пользователе.
    :return:
    None: Выполняет процесс выхода пользователя из системы. В противном случае выбрасывается исключение.
    """
    await user_manager.logout(request, user_agent)
