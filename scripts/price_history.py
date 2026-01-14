#!/usr/bin/env python3
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, text
from app.database import RamPrice, TrackedRam, async_session


async def get_price_history(ram_id: int):
    async with async_session() as session:
        # Check if tracked
        tracked = await session.get(TrackedRam, ram_id)
        if tracked:
            # Query separate table
            table_name = f"ram_{ram_id}_track"
            result = await session.execute(
                text(
                    f"SELECT price, status, scraped_at FROM {table_name} ORDER BY scraped_at"
                )
            )
            rows = result.fetchall()
            print(f"Tracked price history for RAM ID {ram_id}:")
            for row in rows:
                print(f"Date: {row[2].date()}, Price: {row[0]}, Status: {row[1]}")
        else:
            # Query main table (latest only)
            result = await session.execute(
                select(RamPrice).where(RamPrice.ram_id == ram_id)
            )
            price = result.scalar_one_or_none()
            if price:
                print(f"Latest price for RAM ID {ram_id} (not tracked):")
                print(
                    f"Date: {price.scraped_at.date()}, Price: {price.price}, Status: {price.status}"
                )
            else:
                print(f"No price data for RAM ID {ram_id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/price_history.py <ram_id>")
        sys.exit(1)
    ram_id = int(sys.argv[1])
    asyncio.run(get_price_history(ram_id))
