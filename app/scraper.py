import aiohttp
import asyncio
import random
from bs4 import BeautifulSoup
from app.database import RamOption, RamPrice, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple
import re


RANDOM_INTERVALS = [3, 7, 5, 9, 2, 4, 6, 8, 11]


async def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            content = await response.read()
            # Keep as bytes, decode to Big5 later
            return content.decode("big5", errors="ignore")


def parse_option_text(text: str) -> Tuple[str, str, str, str, int, str]:
    # Decode to UTF-8 for processing
    text_utf8 = text.encode("big5").decode("utf-8", errors="ignore")

    # Extract price with regex, e.g., $9499
    price_match = re.search(r"\$([\d,]+)", text_utf8)
    price = int(price_match.group(1).replace(",", "")) if price_match else -99

    # Status: check for "缺貨" (out of stock) or assume in_stock
    status = "out_of_stock" if "缺貨" in text_utf8 else "in_stock"

    # Brand: first word
    parts = text_utf8.split()
    brand = parts[0] if parts else "NaN"

    # Capacity: look for GB
    capacity_match = re.search(r"(\d+GB)", text_utf8)
    capacity = capacity_match.group(1) if capacity_match else "NaN"

    # Speed: DDR5-XXXX
    speed_match = re.search(r"(DDR\d-\d+)", text_utf8)
    speed = speed_match.group(1) if speed_match else "NaN"

    # Latency: /CLXX
    latency_match = re.search(r"/CL(\d+)", text_utf8)
    latency = f"CL{latency_match.group(1)}" if latency_match else "NaN"

    return brand, capacity, speed, latency, price, status


async def scrape_and_store():
    url = "https://www.coolpc.com.tw/evaluate.php"

    # Random delay before request
    interval = random.choice(RANDOM_INTERVALS)
    await asyncio.sleep(interval)

    html_bytes = await fetch_html(url)
    soup = BeautifulSoup(html_bytes, "html.parser")
    select = soup.find("select", {"name": "n6"})
    if not select:
        raise ValueError("RAM select not found")

    options = []
    for optgroup in select.find_all("optgroup"):
        is_dual = "雙q" in optgroup.get("label", "")  # dual channel
        for option in optgroup.find_all("option"):
            if option.get("value") == "0":
                continue  # skip default
            value = int(option.get("value", 0))
            text = option.get_text(strip=True)
            brand, capacity, speed, latency, price, status = parse_option_text(text)
            options.append(
                (value, text, brand, capacity, speed, latency, is_dual, price, status)
            )

    async with get_session() as session:
        for (
            value,
            text,
            brand,
            capacity,
            speed,
            latency,
            is_dual,
            price,
            status,
        ) in options:
            # Upsert option
            ram_option = await session.get(RamOption, value)
            if not ram_option:
                ram_option = RamOption(
                    id=value,
                    name_raw=text,
                    brand=brand,
                    capacity=capacity,
                    speed=speed,
                    latency=latency,
                    is_dual_channel=is_dual,
                )
                session.add(ram_option)
            # Add price entry
            ram_price = RamPrice(ram_id=value, price=price, status=status)
            session.add(ram_price)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(scrape_and_store())
