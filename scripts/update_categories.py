#!/usr/bin/env python3
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import update
from app.database import RamOption, async_session, init_db


async def update_categories():
    await init_db()
    async with async_session() as session:
        # Update RamOption categories based on is_dual_channel
        stmt = (
            update(RamOption)
            .where(RamOption.is_dual_channel == True)
            .values(category="DDR5 雙通")
        )
        await session.execute(stmt)
        stmt2 = (
            update(RamOption)
            .where(RamOption.is_dual_channel == False)
            .values(category="DDR5 單通")
        )
        await session.execute(stmt2)
        await session.commit()
    print("Updated categories.")


if __name__ == "__main__":
    asyncio.run(update_categories())
