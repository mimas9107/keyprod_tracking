# RAM Price Tracking System

A Python-based system to scrape RAM prices from https://www.coolpc.com.tw/evaluate.php, store historical data in SQLite, and provide a FastAPI for querying and charting trends.

## Features

- Daily scraping of RAM options from CoolPC evaluate page.
- Storage of RAM metadata and price history.
- FastAPI endpoints for listing RAM, retrieving price history, and chart data.
- Asynchronous scraping with random delays to simulate human behavior.
- Handles Big5 encoding from source, converts to UTF-8 for internal use.

## Setup

1. Install dependencies:
   ```
   uv sync
   ```

2. Initialize the database:
   ```
   uv run python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
   ```

3. Run the API server:
   ```
   uv run uvicorn app.main:app --reload
   ```

4. Run scraping manually:
   ```
   uv run python scripts/scrape.py
   ```

5. For daily scraping, add to cron:
   ```
   0 2 * * * cd /path/to/project && uv run python scripts/scrape.py
   ```

## API Endpoints

- `GET /ram-options`: List all RAM with latest price.
- `GET /ram/{id}/prices`: Price history for a specific RAM.
- `GET /ram/{id}/chart-data`: JSON data for charting (dates and prices).

## Testing

Run tests:
```
uv run pytest
```

## Data Handling

- Scraped data kept in Big5, parsed to UTF-8.
- Missing prices: -99 (int), "NaN" (str).
- Status: "in_stock" or "out_of_stock".

## Architecture

- `app/database.py`: SQLAlchemy models and session.
- `app/scraper.py`: Async scraping logic.
- `app/main.py`: FastAPI app.
- `scripts/scrape.py`: Entry point for scraping.