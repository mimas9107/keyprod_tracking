#!/usr/bin/env python3
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import TrackedRam, async_session, init_db


async def add_tracked(ram_id: int):
    await init_db()
    async with async_session() as session:
        # Check if already tracked
        existing = await session.get(TrackedRam, ram_id)
        if existing:
            print(f"RAM ID {ram_id} is already tracked.")
            return
        tracked = TrackedRam(ram_id=ram_id)
        session.add(tracked)
        await session.commit()
    print(f"Added RAM ID {ram_id} to tracked list.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/add_tracked.py <ram_id>")
        sys.exit(1)
    ram_id = int(sys.argv[1])
    asyncio.run(add_tracked(ram_id))
