#!/usr/bin/bash
# Frontend 啟動腳本 - 開發模式除錯用
# 原始啟動方式: npm run dev

# 設定顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Frontend 開發伺服器啟動中...${NC}"
echo -e "${GREEN}========================================${NC}"

# 切換到 frontend 目錄
cd "$(dirname "$0")/../frontend" || exit 1

# 檢查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ 未發現 node_modules，正在安裝依賴...${NC}"
    npm install
fi

# 顯示啟動資訊
echo -e "${GREEN}✓ Frontend 目錄: $(pwd)${NC}"
echo -e "${GREEN}✓ 開發伺服器將啟動於: http://localhost:5173${NC}"
echo -e "${YELLOW}ℹ 按 Ctrl+C 停止伺服器${NC}"
echo ""

# 啟動開發伺服器
# 原始指令: npm run dev
npm run dev
