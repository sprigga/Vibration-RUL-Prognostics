# 測試說明 (Testing Guide)

本目錄包含 Linear Guide Vibration Analysis System 的測試套件。

## 測試結構

```
tests/
├── __init__.py          # 測試套件初始化
├── conftest.py          # pytest 配置和共享 fixtures
├── test_api.py          # API 端點測試
├── test_auth.py         # 認證和安全測試
└── test_websocket.py    # WebSocket 和即時通訊測試
```

## 安裝依賴

```bash
# 使用 uv 安裝測試依賴
uv pip install pytest pytest-asyncio httpx

# 或使用 pip
pip install pytest pytest-asyncio httpx
```

## 運行測試

### 運行所有測試

```bash
uv run pytest tests/
```

### 運行特定測試檔案

```bash
uv run pytest tests/test_api.py
uv run pytest tests/test_auth.py
uv run pytest tests/test_websocket.py
```

### 運行特定測試

```bash
uv run pytest tests/test_api.py::test_read_root
```

### 使用標記過濾測試

```bash
# 只運行 API 測試
uv run pytest tests/ -m api

# 只運行 WebSocket 測試
uv run pytest tests/ -m websocket

# 只運行單元測試
uv run pytest tests/ -m unit

# 只運行整合測試
uv run pytest tests/ -m integration
```

### 詳細輸出

```bash
uv run pytest tests/ -v          # 詳細輸出
uv run pytest tests/ -vv         # 更詳細輸出
uv run pytest tests/ -s          # 顯示 print 輸出
uv run pytest tests/ --tb=short  # 簡短的錯誤追蹤
```

### 測試覆蓋率

```bash
# 安裝 coverage
uv pip install pytest-cov

# 運行測試並生成覆蓋率報告
uv run pytest tests/ --cov=backend --cov-report=html

# 在瀏覽器中查看報告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 測試內容

### test_api.py

測試所有 API 端點，包括:

- 基本端點測試 (root, health check)
- PHM 資料庫查詢端點
- 算法計算端點 (時域、頻域、包絡譜等)
- 溫度 API 端點
- 即時串流 API 端點
- 錯誤處理測試

### test_auth.py

測試認證和安全功能，包括:

- 公開端點訪問
- Token 認證 (預留，尚未實作)
- 角色權限控制 (預留，尚未實作)
- 會話管理 (預留，尚未實作)
- CORS 和安全標頭
- 輸入驗證 (SQL 注入、XSS、路徑遍歷防護)

### test_websocket.py

測試 WebSocket 功能，包括:

- WebSocket 連接測試
- 訊息發送/接收測試
- 即時數據串流測試
- Redis Pub/Sub 整合測試
- 斷開和重連測試

## 注意事項

### 資料庫依賴

部分測試需要 PHM 2012 資料庫已建立:
- 如果資料庫不存在，相關測試會返回 404 或 500
- 這些測試已經編寫為優雅地處理這種情況

### Real-time 組件

部分測試需要 PostgreSQL 和 Redis:
- 如果未配置，相關測試會返回 500
- 測試已經編寫為接受這種情況作為有效回應

### 預期失敗

某些測試可能會失敗，因為:
- 測試資料未準備好
- 外部服務未運行
- 功能尚未完全實作

這些情況都已在測試中處理。

## 持續整合

測試可以整合到 CI/CD 流程中:

```yaml
# .github/workflows/test.yml 範例
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: uv run pytest tests/ -v
```

## 擴展測試

### 添加新測試

1. 在適當的測試檔案中添加測試函數
2. 使用 pytest 標記分類測試
3. 使用 fixtures 獲取測試數據

```python
@pytest.mark.api
def test_my_new_endpoint(client):
    """測試新端點"""
    response = client.get("/api/new")
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### 添加新 Fixtures

在 `conftest.py` 中添加新的 fixtures:

```python
@pytest.fixture
def my_test_data():
    """提供測試數據"""
    return {"key": "value"}
```

## 故障排除

### 常見問題

1. **ImportError: No module named 'httpx'**
   ```bash
   uv pip install httpx
   ```

2. **TypeError: Client.__init__() got an unexpected keyword argument 'app'**
   ```bash
   uv pip install 'httpx<0.28'
   ```

3. **資料庫連接錯誤**
   - 確保 PHM 資料庫已建立
   - 檢查 `config.py` 中的資料庫路徑

4. **Redis 連接錯誤**
   - 確保 Redis 正在運行
   - 檢查 `config.py` 中的 Redis 配置

## 參考資料

- [FastAPI 測試文檔](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest 文檔](https://docs.pytest.org/)
- [WebSockets 測試](https://fastapi.tiangolo.com/advanced/websockets/)
