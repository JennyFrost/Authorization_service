from fastapi import Request, FastAPI
from fastapi.responses import PlainTextResponse
from http import HTTPStatus
from fastapi.exceptions import HTTPException

from core.config import Token, Name


class DoesNotExistException(HTTPException):
    def __init__(self, name: Name):
        self.name = name
        self.detail = f'No such {self.name}'
        self.status_code=HTTPStatus.BAD_REQUEST


class AlreadyExistsException(HTTPException):
    def __init__(self, name: Name):
        self.name = name
        self.detail = f'{self.name} already exists'
        self.status_code=HTTPStatus.BAD_REQUEST


class InvalidPasswordException(HTTPException):
    def __init__(self):
        self.detail = 'Wrong password'
        self.status_code=HTTPStatus.BAD_REQUEST


class UnsafeEntryException(HTTPException):
    def __init__(self):
        self.detail = 'Suspicious entry attempt'
        self.status_code = HTTPStatus.BAD_REQUEST


class InvalidTokenException(HTTPException):
    def __init__(self, token: Token):
        self.token = token
        if self.token == Token.BOTH:
            self.detail = 'Access token does not belong to refresh token'
            self.status_code=HTTPStatus.BAD_REQUEST
        else:
            self.detail = 'Signature has expired'
            self.status_code = HTTPStatus.UNPROCESSABLE_ENTITY


class DefaultRoleDoesNotExistException(HTTPException):
    def __init__(self):
        self.detail = 'No default role, can\'t create user'
        self.status_code = HTTPStatus.BAD_REQUEST

# @app.exception_handler(DoesNotExistException)
# async def does_not_exist_handler(request: Request, exc: DoesNotExistException):
#     return PlainTextResponse(f'No such {exc.name}', status_code=HTTPStatus.BAD_REQUEST)
#
#
# @app.exception_handler(AlreadyExistsException)
# async def already_exists_handler(request: Request, exc: AlreadyExistsException):
#     return PlainTextResponse(f'{exc.name} already exists',
#                              status_code=HTTPStatus.BAD_REQUEST)
#
#
# @app.exception_handler(InvalidTokenException)
# async def invalid_token_handler(request: Request, exc: InvalidTokenException):
#     if exc.token == Token.BOTH:
#         return PlainTextResponse('Access token does not belong to refresh token',
#                                  status_code=HTTPStatus.BAD_REQUEST)
#     else:
#         return PlainTextResponse('Signature has expired',
#                                  status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
#
#
# @app.exception_handler(DefaultRoleDoesNotExistException)
# async def default_role_does_not_exist_handler(request: Request, exc: DefaultRoleDoesNotExistException):
#     return PlainTextResponse('No default role, can\'t create user',
#                              status_code=HTTPStatus.BAD_REQUEST)
#
#
# @app.exception_handler(InvalidPasswordException)
# async def invalid_password_handler(request: Request, exc: InvalidPasswordException):
#     return PlainTextResponse('Wrong password',
#                              status_code=HTTPStatus.BAD_REQUEST)
#
#
# @app.exception_handler(UnsafeEntryException)
# async def unsafe_entry_handler(request: Request, exc: UnsafeEntryException):
#     return PlainTextResponse('Suspicious entry',
#                              status_code=HTTPStatus.BAD_REQUEST)
#
#
