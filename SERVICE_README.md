# 人脸识别解锁系统 - 服务化部署指南

## 概述

本系统已升级支持后台服务运行和手机友好的 Web 界面。

## 新功能

### 1. 后台服务运行

- 系统服务化，开机自启动
- 异常自动重启
- 日志记录和管理
- 服务状态监控

### 2. 手机优化界面

- 响应式设计，适配各种屏幕
- 大按钮设计，触摸友好
- 现代化 UI，毛玻璃效果
- 实时状态反馈

## 安装和使用

### 1. 安装系统服务

```bash
# 给脚本执行权限
chmod +x install_service.sh service_manager.sh
# 安装服务
./install_service.sh
```

### 2.服务管理

# 查看服务状态

./service_manager.sh status

# 启动服务

./service_manager.sh start

# 停止服务

./service_manager.sh stop

# 重启服务

./service_manager.sh restart

# 查看实时日志

./service_manager.sh logs

# 启用开机自启

./service_manager.sh enable

# 禁用开机自启

./service_manager.sh disable

### 3. Web 界面访问

安装完成后，可以通过以下地址访问：
http://树莓派 IP:5000
例如：http://192.168.1.100:5000

# 服务特性

## 自动重启

服务异常退出时自动重启
10 秒重启间隔
系统重启后自动启动

## 日志管理

系统日志：sudo journalctl -u face-unlock-web -f
应用日志：logs/ 目录

## 安全配置

非特权用户运行
文件系统保护
最小权限原则

# 手机界面特性

## 响应式设计

自适应屏幕尺寸
横屏/竖屏优化
触摸友好的大按钮

## 现代化 UI

毛玻璃效果背景
渐变色设计
动画和过渡效果
清晰的状态反馈

## 功能按钮

人脸识别解锁：主功能按钮，触发识别
检查系统状态：查看系统运行状态和统计
测试 Mac 服务：测试 Mac 端服务连接

# 故障排除

服务启动失败

# 查看详细错误

sudo journalctl -u face-unlock-web --no-pager -n 50

# 检查文件权限

ls -la /home/pi/face_unlock_system/

# 手动测试

cd /home/pi/face_unlock_system
python3 web_trigger.py

# 网页无法访问

检查服务状态：./service_manager.sh status
检查防火墙设置
确认 IP 地址和端口

# 人脸识别失败

检查摄像头连接
验证模型文件存在：ls -la models/face_model.pkl
检查配置文件：cat config.json
