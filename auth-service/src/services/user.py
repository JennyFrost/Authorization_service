from abc import ABC, abstractmethod
from schemas.entity import UserInDB, UserCreate, UserLogin
from models.entity import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from sqlalchemy import select
from pydantic import BaseModel


class BaseRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def find_user_by_login(self, login):
        pass

    @abstractmethod
    async def create_obj(self, data: BaseModel):
        pass


class BaseUser(BaseRepository):
    async def find_user_by_login(self, login: str) -> User | None:
        query = select(User).filter(User.login == login)
        user = await self.session.execute(query)
        user = user.scalar()
        return user

    async def create_obj(self, data: UserCreate) -> str | None:
        user = await self.find_user_by_login(data.login)
        if user is None:
            new_user = User(
                login=data.login,
                password=data.password,
                last_name=data.last_name,
                first_name=data.first_name
            )
            self.session.add(new_user)
            await self.session.commit()
        else:
            return 'AlreadyExists'

    async def log_in(self, data: UserLogin, Authorize):
        user = await self.find_user_by_login(data.login)
        print(type(user))
        if user is None:
            return 'DoesNotExist'
        if not user.check_password(data.password):
            return 'InvalidPassword'
        # access_token = await Authorize.create_access_token(subject=user.login)
        # return {"access_token": access_token}


    async def get_by_id_obj(self) -> UserInDB | None:
        user = await self.session.get(User, 'c205cd9d-faad-4d7f-9368-c2c26d6126f4')
        if user is not None:
            return UserInDB(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name
            )