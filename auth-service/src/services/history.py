import uuid

from fastapi import Request
from pydantic import BaseModel
# from sqlalchemy.orm.decl_api import DeclarativeMeta


from schemas.entity import UserCreate, UserLogin, UserProfil, ChangeProfil, ChangePassword, FieldFilter, HistoryUser
from models.entity import History as HistoryDB
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.redis_cache import CacheRedis
from services.role import BaseRole
from core.config import app_settings, ErrorName
from time import time
from werkzeug.security import generate_password_hash


class BaseHistory(BaseRepository):
    async def write_entry_history(self, user_id: uuid.UUID, user_agent: str, event_type: str, result: bool):
        await self.create_obj(
            model=HistoryDB,
            data={
                'user_id': user_id,
                'browser': user_agent,
                'event_type': event_type,
                'result': result
            }
        )

    async def get_history(self, user_id: uuid.UUID):
        filter = {"user_id": user_id}
        data_filter = [
            {
                'model': HistoryDB,
                'fields': [
                    FieldFilter(attr_name='user_id', attr_value=str(user_id))
                ]
            },
        ]
        list_obj = await self.get_list_obj_by_list_attr_name_operator_or(data_filter)    
        result = [HistoryUser.parse_obj(obj.__dict__) for obj in list_obj.iterator]
        return result
