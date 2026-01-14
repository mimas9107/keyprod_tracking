#!/usr/bin/env python3
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from app.database import async_session


async def get_tracked_history(ram_id: int):
    async with async_session() as session:
        table_name = f"ram_{ram_id}_track"
        result = await session.execute(
            text(
                f"SELECT price, status, scraped_at FROM {table_name} ORDER BY scraped_at"
            )
        )
        rows = result.fetchall()
        print(f"Tracked price history for RAM ID {ram_id}:")
        for row in rows:
            print(f"Price: {row[0]}, Status: {row[1]}, Scraped: {row[2]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/tracked_history.py <ram_id>")
        sys.exit(1)
    ram_id = int(sys.argv[1])
    asyncio.run(get_tracked_history(ram_id))
