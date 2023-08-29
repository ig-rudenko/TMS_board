from sqlalchemy import select

from .connection import db


class Manager:
    @classmethod
    async def get(cls, id_: int):
        """
        Получение одного элемента.
        """
        query = select(cls).where(cls.id == id_)
        async with db.session as session:
            result = await session.execute(query)
            return result.scalar_one()

    @classmethod
    async def create(cls, **kwargs):
        obj = cls(**kwargs)
        async with db.session as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)  # Получить ID созданного объекта
        return obj

    @classmethod
    async def all(cls):
        """
        Получение всех элементов.
        """
        async with db.session as session:
            result = await session.execute(select(cls))
            return result.scalars().all()
