from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.database import RamOption, RamPrice, TrackedRam, get_session, init_db
from typing import List
from pydantic import BaseModel
from datetime import datetime


# 建立 FastAPI 應用實例，並設定 API 標題
app = FastAPI(title="RAM Price Tracking API")


# --- CORS (跨來源資源共用) 中介軟體設定 ---
# 允許來自前端開發伺服器 (http://localhost:5173) 的請求。
# 這是解決瀏覽器中出現 "NetworkError" 的關鍵。
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 HTTP 標頭
)


# --- Pydantic 回應模型 ---
# 這些模型定義了 API 回應的資料結構，FastAPI 會用它們來驗證、序列化資料並生成 API 文件。


class RamOptionResponse(BaseModel):
    """定義單一 RAM 選項及其最新價格的回應結構"""

    id: int
    name_raw: str
    category: str
    brand: str | None
    capacity: str | None
    speed: str | None
    latency: str | None
    is_dual_channel: bool
    latest_price: int | None
    latest_status: str | None
    latest_scraped_at: datetime | None
    is_tracked: bool


class RamPriceResponse(BaseModel):
    """定義單一價格歷史紀錄的回應結構"""

    price: int
    status: str
    scraped_at: datetime


class ChartDataResponse(BaseModel):
    """定義用於圖表的前端友善資料結構"""

    dates: List[str]
    prices: List[int]


# --- 應用程式生命週期事件 ---


@app.on_event("startup")
async def startup():
    """
    在 FastAPI 應用程式啟動時執行的函數。
    主要工作是初始化資料庫，確保所有資料表都已建立。
    """
    await init_db()


# --- API 端點 (Endpoints) ---


@app.get("/ram-options", response_model=List[RamOptionResponse])
async def get_ram_options(session: AsyncSession = Depends(get_session)):
    """
    獲取所有 RAM 選項及其最新的價格和狀態。
    `session: AsyncSession = Depends(get_session)` 是 FastAPI 的依賴注入，
    它為每個請求提供一個獨立的資料庫 session，並在請求結束後自動關閉。
    """
    # 為了效能優化，這裡使用了一個子查詢來高效地獲取每個 RAM 的最新價格。
    # 1. 建立一個子查詢 (subquery)，找出每個 ram_id 對應的最新 scraped_at 時間點的價格紀錄。
    #    這避免了對每個 RAM 選項都單獨查詢其最新價格所導致的 "N+1 查詢問題"。
    latest_prices_subq = (
        select(RamPrice.ram_id, RamPrice.price, RamPrice.status, RamPrice.scraped_at)
        .distinct(RamPrice.ram_id)
        .order_by(RamPrice.ram_id, RamPrice.scraped_at.desc())
        .subquery()
    )

    # 2. 將 RamOption 表與上面的子查詢進行左外連接 (LEFT OUTER JOIN)。
    #    這樣就可以在一次資料庫查詢中，同時獲得所有 RAM 的詳細資訊以及它們各自的最新價格。
    stmt = (
        select(
            RamOption,
            latest_prices_subq.c.price.label("latest_price"),
            latest_prices_subq.c.status.label("latest_status"),
            latest_prices_subq.c.scraped_at.label("latest_scraped_at"),
            TrackedRam.id.label("tracked_id"),  # If exists, is_tracked = True
        )
        .outerjoin(latest_prices_subq, RamOption.id == latest_prices_subq.c.ram_id)
        .outerjoin(TrackedRam, RamOption.id == TrackedRam.ram_id)
    )

    result = await session.execute(stmt)

    # 3. 將查詢結果組裝成 Pydantic 模型列表。
    rams = []
    for row in result.all(): # 使用 .all() 獲取所有結果
        ram = row.RamOption
        rams.append(
            RamOptionResponse(
                id=ram.id,
                name_raw=ram.name_raw,
                category=ram.category,
                brand=ram.brand,
                capacity=ram.capacity,
                speed=ram.speed,
                latency=ram.latency,
                is_dual_channel=ram.is_dual_channel,
                latest_price=row.latest_price,
                latest_status=row.latest_status,
                latest_scraped_at=row.latest_scraped_at,
                is_tracked=row.tracked_id is not None,
            )
        )
    return rams


@app.get("/ram/{ram_id}/prices", response_model=List[RamPriceResponse])
async def get_ram_prices(ram_id: int, session: AsyncSession = Depends(get_session)):
    """
    根據指定的 ram_id，獲取該 RAM 的所有歷史價格紀錄。
    若為追蹤項目，返回專屬表歷史；否則，返回最新單筆記錄。
    """
    # 檢查是否為追蹤項目
    tracked = await session.get(TrackedRam, ram_id)
    if tracked:
        # 查詢專屬追蹤表
        table_name = f"ram_{ram_id}_track"
        result = await session.execute(
            text(
                f"SELECT price, status, scraped_at FROM {table_name} ORDER BY scraped_at"
            )
        )
        rows = result.fetchall()
        prices = [
            RamPriceResponse(price=row[0], status=row[1], scraped_at=row[2])
            for row in rows
        ]
    else:
        # 查詢主表最新記錄
        stmt = select(RamPrice).where(RamPrice.ram_id == ram_id)
        result = await session.execute(stmt)
        ram_price = result.scalar_one_or_none()
        if ram_price:
            prices = [
                RamPriceResponse(
                    price=ram_price.price,
                    status=ram_price.status,
                    scraped_at=ram_price.scraped_at,
                )
            ]
        else:
            prices = []

    if not prices:
        # 如果找不到任何價格紀錄，回傳 404 錯誤。
        raise HTTPException(status_code=404, detail="RAM not found or no price history")
    return prices


@app.get("/ram/{ram_id}/chart-data", response_model=ChartDataResponse)
async def get_chart_data(ram_id: int, session: AsyncSession = Depends(get_session)):
    """
    根據指定的 ram_id，獲取為前端圖表準備的格式化資料。
    若為追蹤項目，返回專屬表歷史；否則，返回最新單筆記錄。
    """
    # 檢查是否為追蹤項目
    tracked = await session.get(TrackedRam, ram_id)
    if tracked:
        # 查詢專屬追蹤表
        table_name = f"ram_{ram_id}_track"
        result = await session.execute(
            text(f"SELECT scraped_at, price FROM {table_name} ORDER BY scraped_at")
        )
        data = result.fetchall()
    else:
        # 查詢主表最新記錄
        stmt = select(RamPrice.scraped_at, RamPrice.price).where(
            RamPrice.ram_id == ram_id
        )
        result = await session.execute(stmt)
        data = result.fetchall()

    if not data:
        raise HTTPException(status_code=404, detail="RAM not found or no chart data")

    # 將查詢結果的 (日期, 價格) 對，轉換成兩個獨立的列表，方便前端圖表庫使用。
    dates = [d.strftime("%Y-%m-%d %H:%M") for d, _ in data]
    prices = [p for _, p in data]

    return ChartDataResponse(dates=dates, prices=prices)


@app.post("/tracked-rams/{ram_id}")
async def add_to_tracked(ram_id: int, session: AsyncSession = Depends(get_session)):
    """
    將指定的 ram_id 加入追蹤列表。若已存在，返回成功；否則新增。
    """
    # 檢查是否已存在
    existing = await session.get(TrackedRam, ram_id)
    if existing:
        return {"message": "Already tracked", "ram_id": ram_id}

    # 新增追蹤
    tracked = TrackedRam(id=ram_id, ram_id=ram_id)
    session.add(tracked)
    await session.commit()
    return {"message": "Added to tracked", "ram_id": ram_id}
