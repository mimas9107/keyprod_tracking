from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from typing import Optional
from datetime import datetime


class Base(DeclarativeBase):
    pass


class RamOption(Base):
    __tablename__ = "ram_options"

    id: Mapped[int] = mapped_column(primary_key=True)  # option value
    name_raw: Mapped[str]  # raw text in UTF-8
    category: Mapped[str]  # e.g., DDR5, DDR4, etc.
    brand: Mapped[Optional[str]]
    capacity: Mapped[Optional[str]]
    speed: Mapped[Optional[str]]
    latency: Mapped[Optional[str]]
    is_dual_channel: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class RamPrice(Base):
    __tablename__ = "ram_prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ram_id: Mapped[int] = mapped_column(
        unique=True
    )  # FK to RamOption.id, unique for upsert
    price: Mapped[int]  # -99 if missing
    status: Mapped[str]  # e.g., "in_stock", "out_of_stock"
    scraped_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class TrackedRam(Base):
    __tablename__ = "tracked_rams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ram_id: Mapped[int]  # FK to RamOption.id
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


DATABASE_URL = "sqlite+aiosqlite:///./ram_tracking.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
