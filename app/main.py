from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import RamOption, RamPrice, get_session, init_db
from typing import List
from pydantic import BaseModel
from datetime import datetime


app = FastAPI(title="RAM Price Tracking API")


class RamOptionResponse(BaseModel):
    id: int
    name_raw: str
    brand: str | None
    capacity: str | None
    speed: str | None
    latency: str | None
    is_dual_channel: bool
    latest_price: int
    latest_status: str
    latest_scraped_at: datetime


class RamPriceResponse(BaseModel):
    price: int
    status: str
    scraped_at: datetime


class ChartDataResponse(BaseModel):
    dates: List[str]
    prices: List[int]


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/ram-options", response_model=List[RamOptionResponse])
async def get_ram_options(session: AsyncSession = Depends(get_session)):
    # Subquery for latest price per ram
    latest_prices = (
        select(
            RamPrice.ram_id, func.max(RamPrice.scraped_at).label("latest_scraped_at")
        )
        .group_by(RamPrice.ram_id)
        .subquery()
    )

    stmt = select(
        RamOption,
        RamPrice.price.label("latest_price"),
        RamPrice.status.label("latest_status"),
        RamPrice.scraped_at.label("latest_scraped_at"),
    ).join(
        latest_prices,
        (RamOption.id == latest_prices.c.ram_id)
        & (RamPrice.ram_id == latest_prices.c.ram_id)
        & (RamPrice.scraped_at == latest_prices.c.latest_scraped_at),
    )

    result = await session.execute(stmt)
    rams = []
    for row in result:
        ram, price, status, scraped_at = row
        rams.append(
            RamOptionResponse(
                id=ram.id,
                name_raw=ram.name_raw,
                brand=ram.brand,
                capacity=ram.capacity,
                speed=ram.speed,
                latency=ram.latency,
                is_dual_channel=ram.is_dual_channel,
                latest_price=price,
                latest_status=status,
                latest_scraped_at=scraped_at,
            )
        )
    return rams


@app.get("/ram/{ram_id}/prices", response_model=List[RamPriceResponse])
async def get_ram_prices(ram_id: int, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(RamPrice).where(RamPrice.ram_id == ram_id).order_by(RamPrice.scraped_at)
    )
    result = await session.execute(stmt)
    prices = [
        RamPriceResponse(price=p.price, status=p.status, scraped_at=p.scraped_at)
        for p in result.scalars()
    ]
    if not prices:
        raise HTTPException(status_code=404, detail="RAM not found")
    return prices


@app.get("/ram/{ram_id}/chart-data", response_model=ChartDataResponse)
async def get_chart_data(ram_id: int, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(RamPrice.scraped_at, RamPrice.price)
        .where(RamPrice.ram_id == ram_id)
        .order_by(RamPrice.scraped_at)
    )
    result = await session.execute(stmt)
    data = result.fetchall()
    if not data:
        raise HTTPException(status_code=404, detail="RAM not found")
    dates = [d.strftime("%Y-%m-%d") for d, _ in data]
    prices = [p for _, p in data]
    return ChartDataResponse(dates=dates, prices=prices)
