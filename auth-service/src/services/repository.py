from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, Select
from db.postgres import Base


class BaseRepository:
    def __init__(self, session: AsyncSession, **kwargs):
        self.session = session
        super().__init__(**kwargs)

    async def _get_obj(self, query: Select) -> Base | None:
        """
        Выполняет запрос к базе данных и возвращает результат.

        :param query: (Select) Запрос к базе данных, который нужно выполнить.
        :return:
        Base | None: Возвращает результат запроса, который может быть объектом модели или None, если ничего не найдено.
        """
        obj = await self.session.execute(query)
        obj = obj.scalar()
        return obj

    # async def _create_data_filter(self, model, ):

    async def get_obj_by_pk(self, model: Base, pk: int | str) -> Base | None:
        """
        Получает объект из базы данных по его первичному ключу (PK).

        :param model: (Base) Класс модели SQLAlchemy, из которого нужно получить объект.
        :param pk: (int | str) Значение первичного ключа, по которому будет производиться поиск объекта.
        :return:
        Base | None: Возвращает объект из базы данных, соответствующий указанному PK,
                        либо None, если объект не был найден.
        """
        obj = await self.session.get(model, pk)
        return obj

    async def get_obj_by_attr_name(self, model: Base, attr_name: str, attr_value: str | int) -> Base | None:
        """
        Получает объект из базы данных, используя фильтр по имени атрибута и его значению.

        :param model: (Base) Класс модели SQLAlchemy, из которого нужно получить объект.
        :param attr_name: (str) Имя атрибута, по которому будет производиться фильтрация.
        :param attr_value: (str | int) Значение атрибута, по которому будет производиться фильтрация.
        :return:
        Base | None: Возвращает объект из базы данных, соответствующий указанному фильтру,
                    либо None, если объект не был найден.
        """
        query = select(model).filter(getattr(model, attr_name) == attr_value)
        return await self._get_obj(query)

    # async def get_list_obj_by_list_attr_name_or(self, model, ):

    async def get_first_obj_order_by_attr_name(self, model: Base, attr_name: str) -> Base | None:
        """
        Получает первый объект из базы данных, отсортированный по указанному имени атрибута.

        :param model: (Base) Класс модели SQLAlchemy, из которого нужно получить объект.
        :param attr_name: (str) Имя атрибута, по которому будет производиться сортировка.
        :return:
        Base | None: Возвращает первый объект из базы данных, отсортированный по указанному атрибуту,
                     либо None, если объекты не были найдены.
        """
        query = select(model).order_by(getattr(model, attr_name))
        return await self._get_obj(query)

    async def create_obj(self, model: Base, data: dict) -> None:
        """
        Создает и сохраняет новый объект в базе данных.

        :param model: (Base) Класс модели SQLAlchemy, в который будет создан новый объект.
        :param data: (dict) Словарь с данными, используемыми для создания нового объекта.
        :return:
        None: Метод не возвращает значения, а просто сохраняет созданный объект в базе данных.
        """
        new_db_obj = model(
            **data
        )
        self.session.add(new_db_obj)
        await self.session.commit()
