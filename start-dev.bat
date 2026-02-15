@echo off
REM Web B2B 项目启动脚本 - 开发环境

echo ========================================
echo Web B2B 项目启动 - 开发环境
echo ========================================
echo.

REM 设置环境变量
set DJANGO_ENV=development

echo [1/2] 启动 Django 后端...
cd server
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

echo [2/2] 启动 Next.js 前端...
cd ..\web
start "Next.js Server" cmd /k "npm run dev"

echo.
echo ========================================
echo 服务已启动！
echo ========================================
echo.
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:3000
echo.
echo 按任意键关闭此窗口...
pause > nul
