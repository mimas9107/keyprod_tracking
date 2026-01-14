#!/usr/bin/env python3
import asyncio
import sys
import os

LIMIT: int = 1000
# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.database import RamOption, RamPrice, async_session


async def view_data():
    async with async_session() as session:
        # Get all RAM options with latest price
        stmt = select(RamOption).limit(LIMIT)
        result = await session.execute(stmt)
        rams = result.scalars().all()
        print(f"RAM Options (first {LIMIT}):")
        for ram in rams:
            print(
                f"ID: {ram.id}, Category: {ram.category}, Name: {ram.name_raw}, Brand: {ram.brand}, Capacity: {ram.capacity}, Speed: {ram.speed}, Latency: {ram.latency}"
            )

        # Get all prices
        stmt_prices = select(RamPrice).limit(LIMIT)
        result_prices = await session.execute(stmt_prices)
        prices = result_prices.scalars().all()
        print(f"\nPrices (first {LIMIT}):")
        for price in prices:
            print(
                f"RAM ID: {price.ram_id}, Price: {price.price}, Status: {price.status}, Scraped: {price.scraped_at}"
            )

    print("Done viewing data.")


if __name__ == "__main__":
    asyncio.run(view_data())
