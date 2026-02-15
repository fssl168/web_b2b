@echo off
REM Web B2B 项目启动脚本 - 生产环境

echo ========================================
echo Web B2B 项目启动 - 生产环境
echo ========================================
echo.

REM 设置环境变量
set DJANGO_ENV=production

echo 检查配置...

REM 检查是否配置了正确的SECRET_KEY
cd server
findstr /C:"your-secret-key-change-this-in-production" .env.production > nul
if %errorlevel% equ 0 (
    echo.
    echo [警告] 请先修改 .env.production 中的 SECRET_KEY！
    echo 当前使用默认值不安全。
    echo.
    echo 按任意键继续...
    pause > nul
)

echo.
echo [1/2] 启动 Django 后端...
REM 生产环境使用 gunicorn（需要安装）
REM gunicorn --workers 4 --bind 0.0.0.0:8000 server.wsgi:application
python manage.py runserver 0.0.0.0:8000 --settings=server.settings

echo.
echo ========================================
echo 服务已启动！
echo ========================================
