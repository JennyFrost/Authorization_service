import uuid

from schemas.entity import HistoryUser
from models.entity import History
from services.repository import BaseRepository


class BaseHistory(BaseRepository):
    async def write_entry_history(self, user_id: uuid.UUID, user_agent: str, event_type: str, result: bool):
        await self.create_obj(
            model=History,
            data={
                'user_id': user_id,
                'browser': user_agent,
                'event_type': event_type,
                'result': result
            }
        )

    async def get_history(self, user_id: uuid.UUID, page_number: int, page_size: int):
        list_obj = await self.get_list_obj_by_attr_name(model=History, attr_name='user_id', attr_value=user_id,
                                                  page_number=page_number, page_size=page_size)
        result = [HistoryUser.model_validate(obj.__dict__) for obj in list_obj]
        return result
