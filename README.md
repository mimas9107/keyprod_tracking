# RAM 價格追蹤系統

一個基於 Python 的系統，用於從目標網站抓取 RAM 價格，儲存歷史資料至 SQLite，並提供 FastAPI 介面查詢與圖表趨勢。前端使用 React 展示卡片式清單與圖表。

## 功能特點

- 每日自動抓取 CoolPC 評估頁面的 RAM 選項與價格。
- 儲存 RAM 中繼資料與價格歷史記錄。
- FastAPI 端點用於列出 RAM、取得價格歷史與圖表資料。
- 非同步抓取，隨機延遲模擬人類行為，避免被封鎖。
- 處理來源的 Big5 編碼，內部轉換為 UTF-8。
- 前端 React 介面：卡片式清單展示（每頁 50 個）、搜尋、排序、分頁。
- 追蹤功能：使用者可將特定 RAM 加入追蹤，儲存長期歷史價格。
- 價格趨勢圖表：點擊卡片查看歷史價格線圖。

## 系統需求

- Python 3.13+
- Node.js (前端開發)
- SQLite (資料庫)

## 安裝與設定

### 後端設定

1. 安裝相依套件：
   ```
   uv sync
   ```

2. 初始化資料庫：
   ```
   uv run python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
   ```

3. 啟動 API 伺服器：
   ```
   uv run uvicorn app.main:app --reload
   ```
   伺服器將在 `http://127.0.0.1:8000` 運行。

4. 手動執行抓取：
   ```
   uv run python scripts/scrape.py
   ```

5. 設定每日自動抓取（加入 cron）：
   ```
   0 2 * * * cd /path/to/project && uv run python scripts/scrape.py
   ```

### 前端設定

1. 安裝前端相依套件：
   ```
   cd frontend
   npm install
   ```

2. 啟動開發伺服器：
   ```
   npm run dev
   ```
   前端將在 `http://localhost:5173` 運行。

3. 建構生產版本：
   ```
   npm run build
   ```

## 使用方法

### 快速啟動
- Windows：雙擊 `start.bat` 啟動系統，雙擊 `stop.bat` 停止（需手動建立）。
- Linux/Mac：執行 `./start.sh` 啟動，`./stop.sh` 停止。

### 後端腳本

- `scripts/scrape.py`：手動抓取資料。
- `scripts/view_data.py`：檢視 RAM 選項與價格。
- `scripts/price_history.py <ram_id>`：查看特定 RAM 的價格歷史。
- `scripts/tracked_history.py <ram_id>`：查看追蹤 RAM 的歷史。
- `scripts/add_tracked.py <ram_id>`：加入 RAM 至追蹤列表。

### 前端操作

1. 開啟瀏覽器訪問 `http://localhost:5173`。
2. 搜尋欄：輸入名稱篩選 RAM。
3. 排序下拉選單：依品牌、名稱、容量等排序。
4. 卡片清單：每張卡片顯示 RAM 資訊（1-2 行），點擊查看價格趨勢圖表。
5. 追蹤按鈕：點擊加入追蹤，已追蹤的按鈕會停用。
6. 分頁：每頁顯示 50 個 RAM。

## API 文件

- `GET /ram-options`：列出所有 RAM 及其最新價格、追蹤狀態。
  - 回應範例：
    ```json
    [
      {
        "id": 1,
        "name_raw": "UMAX 32GB...",
        "brand": "UMAX",
        "capacity": "32GB",
        "speed": "DDR5-4800",
        "latency": "CL40",
        "latest_price": 9499,
        "latest_status": "in_stock",
        "latest_scraped_at": "2023-10-01T12:00:00",
        "is_tracked": false
      }
    ]
    ```

- `GET /ram/{id}/prices`：取得特定 RAM 的價格歷史（追蹤項目返回累積歷史，非追蹤返回最新）。
  - 回應範例：
    ```json
    [
      {
        "price": 9499,
        "status": "in_stock",
        "scraped_at": "2023-10-01T12:00:00"
      }
    ]
    ```

- `GET /ram/{id}/chart-data`：取得圖表資料（日期與價格）。
  - 回應範例：
    ```json
    {
      "dates": ["2023-10-01 12:00", "2023-10-02 12:00"],
      "prices": [9499, 9599]
    }
    ```

- `POST /tracked-rams/{id}`：將 RAM 加入追蹤列表。
  - 回應範例：
    ```json
    {
      "message": "Added to tracked",
      "ram_id": 1
    }
    ```

## 測試

執行測試：
```
uv run pytest
```

前端檢查：
```
cd frontend && npm run lint
```

## 資料處理

- 抓取資料以 Big5 保留，解析後轉為 UTF-8。
- 缺價格：-99 (整數)，"NaN" (字串)。
- 狀態："in_stock" 或 "out_of_stock"。

## 架構

- `app/database.py`：SQLAlchemy 模型與會話。
- `app/scraper.py`：非同步抓取邏輯。
- `app/main.py`：FastAPI 應用程式。
- `frontend/src/App.jsx`：React 根元件。
- `frontend/src/components/RamTable.jsx`：卡片清單元件。
- `frontend/src/components/PriceHistoryChart.jsx`：圖表模態元件。
- `scripts/`：實用腳本。

## 授權

本專案僅供學習與個人使用，請遵守網站使用條款。
