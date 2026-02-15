@echo off
REM 数据库迁移脚本
REM 用于应用安全加固的数据库变更

echo ========================================
echo Web B2B 安全加固 - 数据库迁移
echo ========================================
echo.

REM 切换到server目录
cd server

echo [1/2] 检查Django环境...
python manage.py --version
if %errorlevel% neq 0 (
    echo ❌ Django环境检查失败
    pause
    exit /b 1
)
echo ✅ Django环境正常
echo.

echo [2/2] 执行数据库迁移...
python manage.py migrate myapp
if %errorlevel% neq 0 (
    echo ❌ 数据库迁移失败
    pause
    exit /b 1
)
echo ✅ 数据库迁移成功
echo.

echo ========================================
echo 迁移完成！
echo ========================================
echo.
echo 下一步：
echo 1. 安装新的依赖：pip install -r requirements.txt
echo 2. 重新构建前端：cd ..\web ^&^& npm run build
echo 3. 启动服务：
echo    - 后端：cd server ^&^& python manage.py runserver
echo    - 前端：cd web ^&^& npm run start
echo.
pause
