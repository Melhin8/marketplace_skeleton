import uuid

from sqlalchemy import Column, DateTime, func, Integer, Numeric, String, Text
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

from api.database import Base, db


class AsyncCRUD():
    @staticmethod
    async def try_commit(db):
        # Obj.try_commit()
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.add(obj)
        await cls.try_commit(db)
        return obj
    
    @classmethod
    async def update(cls, id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.try_commit(db)

    @classmethod
    async def get(cls, id):
        query = select(cls).where(cls.id == id)
        obj = await db.execute(query)
        (user,) = obj.first()
        return user

    @classmethod
    async def get_all(cls):
        query = select(cls)
        obj = await db.execute(query)
        obj = obj.scalars().all()
        return obj

    @classmethod
    async def delete(cls, id):
        query = sqlalchemy_delete(cls).where(cls.id == id)
        await db.execute(query)
        await cls.try_commit(db)
        return True


class User(Base, AsyncCRUD):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    hashed_pasword = Column(String)
    stores = relationship("Store", backref="users")
    orders = relationship("Orders", backref="users")


class Store(Base, AsyncCRUD):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    owner_id = Column(ForeignKey("users.id")) # type: ignore


class Product(Base, AsyncCRUD):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(ForeignKey("stores.id"), nullable=False) # type: ignore
    store = relationship("Store", backref="products")
    name = Column(Text, nullable=False)
    price = Column(Numeric(12, 2), nullable=False) # type: ignore

    __table_args__ = (UniqueConstraint("name", "store_id", name="uix_products"),)


class Order(Base, AsyncCRUD):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, server_default=func.now(), nullable=False)
    items = relationship("OrderItem", backref="order")
    owner_id = Column(ForeignKey("users.id")) # type: ignore


class OrderItem(Base, AsyncCRUD):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(ForeignKey("orders.order_id"), primary_key=True) # type: ignore
    product_id = Column(ForeignKey("products.product_id"), primary_key=True) # type: ignore
    product = relationship("Product", uselist=False)
    quantity = Column(Integer, nullable=False)