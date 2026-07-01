#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}  BUPT 智能充电桩调度计费系统${NC}"
echo ""

# Python environment
echo -e "${YELLOW}[1/4] 配置 Python 环境...${NC}"
UVS_ACTIVATE="$HOME/.uvs_envs/base/bin/activate"
if [ -f "$UVS_ACTIVATE" ]; then
    source "$UVS_ACTIVATE"
    echo -e "${GREEN}  ✓ uvs base ($(python --version))${NC}"
elif command -v python3 &> /dev/null; then
    alias python=python3
    echo -e "${GREEN}  ✓ system python3 ($(python3 --version))${NC}"
else
    echo "  ✗ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

# Backend deps
echo -e "${YELLOW}[2/4] 安装后端依赖...${NC}"
cd "$BACKEND_DIR"
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt --quiet 2>/dev/null
else
    python -m pip install -r requirements.txt --quiet 2>/dev/null
fi
echo -e "${GREEN}  ✓ 后端依赖就绪${NC}"

# Frontend deps
echo -e "${YELLOW}[3/4] 安装前端依赖...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install --silent 2>/dev/null
fi
echo -e "${GREEN}  ✓ 前端依赖就绪${NC}"

# Start services
echo -e "${YELLOW}[4/4] 启动服务...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

cd "$BACKEND_DIR"
[ -f "$UVS_ACTIVATE" ] && source "$UVS_ACTIVATE"
python -m uvicorn app.main:app --reload --port 8000 > /tmp/charging_backend.log 2>&1 &
sleep 2

if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 后端已启动 :8000${NC}"
else
    echo "  ✗ 后端启动失败，查看 /tmp/charging_backend.log"
    exit 1
fi

cd "$FRONTEND_DIR"
npx vite --port 3000 > /tmp/charging_frontend.log 2>&1 &
sleep 2
echo -e "${GREEN}  ✓ 前端已启动 :3000${NC}"

echo ""
echo -e "  前端: ${GREEN}http://localhost:3000${NC}"
echo -e "  API:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  账号: admin / admin123"
echo ""
