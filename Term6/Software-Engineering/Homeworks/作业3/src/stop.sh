#!/bin/bash
# 停止充电桩系统所有服务

pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "所有服务已停止"
