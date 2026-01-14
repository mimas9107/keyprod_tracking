#!/usr/bin/env python3
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.database import RamPrice, async_session


async def get_price_history(ram_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(RamPrice)
            .where(RamPrice.ram_id == ram_id)
            .order_by(RamPrice.scraped_at)
        )
        prices = result.scalars().all()
        print(f"Price history for RAM ID {ram_id}:")
        for price in prices:
            print(
                f"Date: {price.scraped_at.date()}, Price: {price.price}, Status: {price.status}"
            )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/price_history.py <ram_id>")
        sys.exit(1)
    ram_id = int(sys.argv[1])
    asyncio.run(get_price_history(ram_id))
