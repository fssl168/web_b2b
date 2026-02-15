# Debian 环境启动脚本

## 使用说明

这两个脚本是为 Debian/Ubuntu 环境设计的，用于替代 Windows 批处理文件。

### 开发环境启动脚本 (start-dev.sh)

```bash
./start-dev.sh
```

此脚本将：
1. 设置 DJANGO_ENV=development 环境变量
2. 在新终端窗口中启动 Django 后端 (端口 8000)
3. 在新终端窗口中启动 Next.js 前端 (端口 3000)

### 生产环境启动脚本 (start-prod.sh)

```bash
./start-prod.sh
```

此脚本将：
1. 设置 DJANGO_ENV=production 环境变量
2. 检查 .env.production 中的 SECRET_KEY 是否已更改
3. 启动 Django 后端 (端口 8000)

## 使用前准备

1. 确保已安装 Python 和 Node.js
2. 在 Debian/Ubuntu 系统上，给脚本添加可执行权限：
   ```bash
   chmod +x start-dev.sh start-prod.sh
   ```

## 注意事项

- 如果系统没有安装 gnome-terminal，脚本中已提供使用 xterm 的替代方案（注释状态）
- 生产环境中建议使用 gunicorn 而不是 Django 开发服务器
- 确保已安装所有必要的依赖项
- 脚本使用了安全的目录导航方式，如果目录不存在会立即退出