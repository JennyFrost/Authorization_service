from fastapi import Request

from schemas.entity import UserCreate, UserLogin, UserProfil, ChangeProfil, ChangePassword, FieldFilter
from models.entity import User, Role, EventEnum
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.history import BaseHistory
from services.redis_cache import CacheRedis
from services.role import BaseRole
from core.config import app_settings, Token, Name
from time import time
from werkzeug.security import generate_password_hash
from core.exceptions import *


class BaseAuth(BaseRepository, BaseAuthJWT, CacheRedis):

    def __init__(self, manager_history: BaseHistory, *args, **kwargs):
        self.manager_history = manager_history
        super().__init__(*args, **kwargs)

    async def sign_up(self, data: UserCreate) -> None:
        """
        Регистрирует нового пользователя.

        :param data: (UserCreate) Данные, необходимые для создания нового пользователя.
        :return:
        None: Возвращает None, если регистрация прошла успешно.
        В противном случае выбрасывается исключение.
        """
        data_filter = [
            {
                'model': User,
                'fields': [
                    FieldFilter(attr_name='login', attr_value=data.login),
                    FieldFilter(attr_name='email', attr_value=data.email)
                ]
            },
        ]
        users = await self.get_list_obj_by_list_attr_name_operator_or(data_filter)
        for user in users:
            if user.login == data.login:
                raise AlreadyExistsException(name=Name.LOGIN)
            if user.email == data.email:
                raise AlreadyExistsException(name=Name.EMAIL)

        role = await self.get_first_obj_order_by_attr_name(Role, 'lvl')
        if role is None:
            role_manager = BaseRole(self.session)
            await role_manager.create_default_role()
            role = await self.get_first_obj_order_by_attr_name(Role, 'lvl')

        await self.create_obj(
            model=User,
            data={
                'login': data.login,
                'password': data.password,
                'last_name': data.last_name,
                'first_name': data.first_name,
                'email': data.email,
                'role': role
            }
        )

    async def log_in(self, data: UserLogin, user_agent: str) -> None:
        """
         Авторизация и аутентификация пользователя и создание токенов.

        :param data: (UserLogin) Данные, необходимые для аутентификации пользователя (логин и пароль).
        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        :return:
        None: Возвращает None, если аутентификация прошла успешно.
        В противном случае выбрасывается исключение.
        """
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            raise DoesNotExistException(name=Name.USER)
        elif not user.check_password(data.password):
            raise InvalidPasswordException()
        _, refresh_token = await self.create_tokens(sub=str(user.id), user_claims={
            'user_agent': user_agent,
            'is_admin': user.is_admin
            })
        await self._put_object_to_cache(obj=refresh_token, time_cache=app_settings.authjwt_time_refresh)
        result = True
        await self.manager_history.write_entry_history(
            user_id=user.id,
            user_agent=user_agent,
            event_type=EventEnum.login,
            result=result
        )


    async def get_info_from_access_token(self, user_agent: str) -> dict:
        """
        Получает информацию из access token и проверяет его безопасность.

        :param user_agent: (str) Заголовок User-Agent, для сравнения с данными из access token.
        :return:
        dict: Возвращает словарь с информацией из access token.
        В противном случае выбрасывается исключение.
        """
        user_data = await self.check_access_token()
        if await self._object_from_cache(obj=user_data.get('jti')):
            raise InvalidTokenException(token=Token.ACCESS)
        elif user_agent != user_data.get('user_agent'):
            time_cache = user_data.get('exp', int(time())) - int(time())
            await self._put_object_to_cache(obj=user_data.get('jti'), time_cache=time_cache)
            raise UnsafeEntryException()
        else:
            return user_data

    async def refresh_token(self, user_agent: str, request: Request) -> None:
        """
            Обновляет access token и возвращает его.

        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        :param request: (Request) Объект запроса, содержащий cookies с refresh token и access token.
        :return:
        str: Возвращает обновленный access token, если все проверки прошли успешно.
        В противном случае выбрасывается исключение.
        """
        refresh_token = request.cookies.get(app_settings.authjwt_refresh_cookie_key)
        if not await self._object_from_cache(obj=refresh_token):
            raise InvalidTokenException(token=Token.REFRESH)

        await self._delete_object_from_cache(obj=refresh_token)
        uuid_access = request.cookies.get(app_settings.authjwt_access_cookie_key).split('.')[-1]
        data = await self.check_refresh_token()
        if data.get('user_agent', '') != user_agent:
            raise UnsafeEntryException()
        elif data.get('uuid_access', '') != uuid_access:
            raise InvalidTokenException(token=Token.BOTH)
        _, refresh_token = await self.create_tokens(
            sub=data.get('sub'),
            user_claims={
                'user_agent': user_agent,
                'is_admin': data.get('is_admin')
                })
        await self._put_object_to_cache(refresh_token, app_settings.authjwt_time_refresh)
        result = True
        await self.manager_history.write_entry_history(
            user_id=data.get('sub'),
            user_agent=user_agent,
            event_type=EventEnum.refresh,
            result=result
        )
        return

    async def logout(self, request: Request, user_agent: str) -> None:
        """
        Осуществляет выход пользователя из системы (logout).

        :param request: (Request) Объект запроса, содержащий cookies с данными о пользователе.
        :return:
        None: Метод не возвращает значения, а просто выполняет процесс выхода пользователя из системы.
        В противном случае выбрасывается исключение.
        """
        user_data = await self.check_access_token()
        time_cache = user_data.get('exp', int(time())) - int(time())
        await self._put_object_to_cache(obj=user_data.get('jti'), time_cache=time_cache)

        refresh_token = request.cookies.get(app_settings.authjwt_refresh_cookie_key)
        await self._delete_object_from_cache(obj=refresh_token)

        await self.jwt_logout()

        await self.manager_history.write_entry_history(
            user_id=user_data.get('sub'),
            user_agent=user_agent,
            event_type=EventEnum.logout,
            result=True
        )


class UserManage:
    '''
    Класс для управления личным кабинетом пользователя
    '''

    def __init__(self, manager_auth: BaseAuth, manager_role: BaseRole, manager_history: BaseHistory):
        self.manager_auth = manager_auth
        self.manager_role = manager_role
        self.manager_history = manager_history

    async def get_history(self, user_agent: str, page_number, page_size):
        '''
        Метод для получения истории

        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        '''

        user_obj: User = await self.get_user_obj(user_agent)
        if not isinstance(user_obj, User):
            return user_obj
        result = await self.manager_history.get_history(user_obj.id, page_number, page_size)
        return result

    async def change_level(self, user_agent: str, level_up=True):
        '''
        Метод для изменения уровня подписки пользователя

        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        :param level_up: (bool) Параметр для понижения уровня подписки при False или для повышения при True.
        '''
        user_obj: User = await self.get_user_obj(user_agent)
        if not isinstance(user_obj, User):
            return user_obj
        if level_up:
            role_lvl_new = user_obj.role.lvl + 1
        else:
            role_lvl_new = user_obj.role.lvl - 1
        role_obj_higher = await self.manager_auth.get_obj_by_attr_name(Role, 'lvl', role_lvl_new)
        if role_obj_higher:
            user_obj.role = role_obj_higher
            await self.manager_auth.session.commit()
        else:
            raise DoesNotExistException(name=Name.ROLE)

    async def change_password(self, user_agent: str, new_data: ChangePassword):
        '''
        Метод для изменения пароля пользователя
        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        '''

        user_obj: User = await self.get_user_obj(user_agent)
        if not isinstance(user_obj, User):
            return user_obj
        if not user_obj.check_password(new_data.old_password):
            raise InvalidPasswordException()
        user_obj.password = generate_password_hash(new_data.new_password)
        await self.manager_auth.session.commit()

    async def get_user_data(self, user_agent: str):
        '''
        Метод для получения информации о пользователе.
        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        '''

        user_obj: User = await self.get_user_obj(user_agent)
        if not isinstance(user_obj, User):
            return user_obj
        user_profil = await self.get_user_profil(user_obj)
        return user_profil

    async def change_profile_user(self, user_agent: str, new_data: ChangeProfil):
        '''
        Метод для изменения информации о пользователе
        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        '''

        user_obj: User = await self.get_user_obj(user_agent)
        if not isinstance(user_obj, User):
            return user_obj
        data_check = dict()
        if new_data.first_name:
            user_obj.first_name = new_data.first_name
        if new_data.last_name:
            user_obj.last_name = new_data.last_name

        if new_data.email and new_data.login != user_obj.login:
            data_check["email"] = new_data.email
        if new_data.login and new_data.email != user_obj.email:
            data_check["login"] = new_data.login

        await self.search_for_duplicates(data_check)

        if new_data.email:
            user_obj.email = new_data.email
        if new_data.login:
            user_obj.login = new_data.login

        await self.manager_auth.session.commit()

        user_profil = await self.get_user_profil(user_obj)
        return user_profil

    async def get_user_profil(self, user_obj: User) -> UserProfil:
        profil = UserProfil(
            login=user_obj.login,
            first_name=user_obj.first_name,
            last_name=user_obj.last_name,
            name_role=f"{user_obj.role.lvl}:{user_obj.role.name_role}",
            email=user_obj.email
        )
        return profil

    async def get_user_obj(self, user_agent: str):
        user_data = await self.manager_auth.get_info_from_access_token(user_agent)
        if not isinstance(user_data, dict):
            return user_data
        user_id = user_data.get("sub")
        user_obj: User = await self.manager_auth.get_obj_by_pk(User, user_id)
        return user_obj

    async def search_for_duplicates(self, data: dict) -> None:
        fields = [FieldFilter(attr_name=key, attr_value=item) for key, item in data.items()]
        data_filter = [
            {
                'model': User,
                'fields': fields
            },
        ]
        users = await self.manager_auth.get_list_obj_by_list_attr_name_operator_or(data_filter)
        for user in users:
            if user.login == data.get("login"):
                raise AlreadyExistsException(name=Name.LOGIN)
            if user.email == data.get("email"):
                raise AlreadyExistsException(name=Name.EMAIL)
