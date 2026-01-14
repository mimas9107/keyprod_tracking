#!/usr/bin/env python3
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.scraper import scrape_and_store

if __name__ == "__main__":
    asyncio.run(scrape_and_store())
    print("Scraping completed.")
