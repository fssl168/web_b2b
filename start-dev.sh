#!/bin/bash
# Web B2B 项目启动脚本 - 开发环境

echo "========================================"
echo "Web B2B 项目启动 - 开发环境"
echo "========================================"
echo

# 设置环境变量
export DJANGO_ENV=development

echo "[1/2] 启动 Django 后端..."
cd server || exit 1
gnome-terminal -- bash -c "python manage.py runserver 0.0.0.0:8000; exec bash" &
# 或者使用 xterm 如果没有 gnome-terminal
# xterm -e "python manage.py runserver 0.0.0.0:8000" &

echo "[2/2] 启动 Next.js 前端..."
cd ../web || exit 1
gnome-terminal -- bash -c "npm run dev; exec bash" &
# 或者使用 xterm 如果没有 gnome-terminal
# xterm -e "npm run dev" &

echo
echo "========================================"
echo "服务已启动！"
echo "========================================"
echo
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:3000"
echo
echo "按 Ctrl+C 停止服务..."