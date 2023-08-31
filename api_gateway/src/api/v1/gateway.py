from typing import Annotated
from fastapi import APIRouter, Header, Response, Request
import aiohttp

from core.config import app_settings
from schemas.entity import UserLogin, UserCreate

router = APIRouter()


@router.post('/login/')
async def login(response: Response, data: UserLogin, user_agent: Annotated[str | None, Header()] = None):
    url = f'{app_settings.auth_url}/api/v1/auth/login/'
    headers = {
        'User-Agent': user_agent,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data.dict(), headers=headers) as resp:
            for cookie in resp.cookies.items():
                response.set_cookie(key=cookie[0], value=cookie[1])
            return resp.json()


@router.post('/sign_up/')
async def sign_up(data: UserCreate):
    url = f'{app_settings.auth_url}/api/v1/auth/sign_up/'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data.dict()) as resp:
            return resp.json()


@router.get('/get_user/')
async def get_user(request: Request, user_agent: Annotated[str | None, Header()] = None):
    url = f'{app_settings.auth_url}/api/v1/auth/get_user/'
    headers = {
        'User-Agent': user_agent,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, cookies=request.cookies) as resp:
            return resp.json()


@router.post('/refresh/')
async def refresh(request: Request, response: Response, user_agent: Annotated[str | None, Header()] = None):
    url = f'{app_settings.auth_url}/api/v1/auth/refresh/'
    headers = {
        'User-Agent': user_agent,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, cookies=request.cookies) as resp:
            for cookie in resp.cookies.items():
                response.set_cookie(key=cookie[0], value=cookie[1])
            return resp.json()
