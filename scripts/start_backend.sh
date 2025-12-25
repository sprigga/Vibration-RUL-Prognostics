#!/usr/bin/bash
# Backend 啟動腳本 - 開發模式除錯用
# 原始啟動方式: uv run uvicorn backend.main:app --reload --port 8000

# 設定顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Backend API 伺服器啟動中...${NC}"
echo -e "${GREEN}========================================${NC}"

# 切換到專案根目錄
cd "$(dirname "$0")/.." || exit 1

# 檢查 uv 是否安裝
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ 錯誤: uv 未安裝${NC}"
    echo -e "${YELLOW}請先安裝 uv: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# 檢查 .venv 是否存在
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ 未發現 .venv，正在建立虛擬環境...${NC}"
    uv venv
fi

# 顯示啟動資訊
echo -e "${GREEN}✓ 專案根目錄: $(pwd)${NC}"
echo -e "${GREEN}✓ API 文件: http://localhost:8000/docs${NC}"
echo -e "${GREEN}✓ API 端點: http://localhost:8000${NC}"
echo -e "${YELLOW}ℹ 按 Ctrl+C 停止伺服器${NC}"
echo ""

# 啟動 FastAPI 開發伺服器 (含自動重新載入)
# 原始指令: uv run uvicorn backend.main:app --reload --port 8000
uv run uvicorn backend.main:app --reload --port 8000
