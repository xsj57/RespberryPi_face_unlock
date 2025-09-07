# 🚀 树莓派人脸识别解锁系统 - 完整部署指南

本指南将详细介绍如何从零开始在树莓派上部署人脸识别解锁系统。

## 📋 目录

1. [硬件准备](#-硬件准备)
2. [系统环境配置](#-系统环境配置)
3. [项目部署](#-项目部署)
4. [Mac 端配置](#-mac端配置)
5. [系统服务配置](#-系统服务配置)
6. [测试验证](#-测试验证)
7. [常见问题解决](#-常见问题解决)
8. [安全配置](#-安全配置)

## 🛠 硬件准备

### 必需硬件

- **树莓派 4B/5**（推荐 8GB 内存版本）
- **MicroSD 卡**（32GB 以上，Class 10）
- **树莓派摄像头**
  - 官方摄像头模块 V2/V3
  - 或 USB 摄像头（支持 UVC）
- **电源适配器**（5V 3A）
- **网络连接**（WiFi 或有线网络）

### 可选硬件

- **外壳**（带摄像头固定支架）
- **散热片/风扇**（提升性能）
- **LED 指示灯**（GPIO 连接，状态指示）

## 💻 系统环境配置

### 1. 安装树莓派操作系统

使用 Raspberry Pi Imager 安装最新的 Raspberry Pi OS（推荐 Lite 版本）：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git vim curl wget htop
```

### 2. 启用摄像头

```bash
# 方法1：使用raspi-config
sudo raspi-config
# 选择 Interface Options -> Camera -> Enable

# 方法2：编辑配置文件
echo 'camera_auto_detect=1' | sudo tee -a /boot/config.txt
echo 'dtoverlay=ov5647' | sudo tee -a /boot/config.txt

# 重启系统
sudo reboot
```

### 3. 安装 Python 环境

```bash
# 安装Python和pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 安装编译工具（face_recognition需要）
sudo apt install -y build-essential cmake pkg-config

# 安装OpenCV依赖
sudo apt install -y libopencv-dev python3-opencv

# 安装图像处理库
sudo apt install -y libjpeg-dev libtiff5-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev

# 安装数学库
sudo apt install -y libatlas-base-dev gfortran
```

### 4. 安装 rpicam 工具

```bash
# 安装最新的rpicam工具
sudo apt install -y rpicam-apps

# 测试摄像头
rpicam-hello -t 2000
```

## 📦 项目部署

### 1. 克隆项目

```bash
# 克隆项目到用户目录
cd ~
git clone <your-github-repo-url> face_unlock_system
cd face_unlock_system
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 3. 安装 Python 依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 如果face_recognition安装失败，尝试预编译版本
sudo apt install -y python3-face-recognition
# 然后在虚拟环境中创建链接
ln -s /usr/lib/python3/dist-packages/face_recognition venv/lib/python3.*/site-packages/
```

### 4. 配置系统

```bash
# 复制配置模板
cp config.template.json config.json

# 编辑配置文件
nano config.json
```

关键配置项：

```json
{
  "mac": {
    "enabled": true,
    "host": "你的Mac的IP地址或主机名",
    "port": 5001,
    "username": "你的Mac用户名",
    "password": "你的Mac密码"
  },
  "authorized_users": ["你的用户名"],
  "web": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 5000
  }
}
```

### 5. 创建必要目录

```bash
# 创建数据目录
mkdir -p faces models logs

# 设置权限
chmod 755 faces models logs
```

## 🍎 Mac 端配置

### 1. 下载 Mac 解锁服务

在 Mac 上创建解锁服务脚本：

```python
# mac_unlock_service.py
#!/usr/bin/env python3
from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/status')
def status():
    return jsonify({'status': 'running', 'service': 'mac-unlock'})

@app.route('/unlock', methods=['POST'])
def unlock():
    data = request.get_json()
    if data.get('key') == 'face_unlock_2024':
        try:
            # 模拟键盘输入解锁密码
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "你的密码"'])
            return jsonify({'status': 'success', 'message': 'Mac unlocked'})
        except:
            return jsonify({'status': 'error', 'message': 'Unlock failed'}), 500
    return jsonify({'status': 'unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### 2. 安装 Mac 端依赖

```bash
# 在Mac上安装Flask
pip3 install flask

# 运行解锁服务
python3 mac_unlock_service.py
```

### 3. 设置 Mac 端自启动

创建 plist 文件：

```xml
<!-- ~/Library/LaunchAgents/com.faceunlock.mac.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.faceunlock.mac</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/mac_unlock_service.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

加载服务：

```bash
launchctl load ~/Library/LaunchAgents/com.faceunlock.mac.plist
```

## 👤 人脸数据采集和训练

### 1. 采集人脸数据

```bash
# 确保在项目目录和虚拟环境中
cd ~/face_unlock_system
source venv/bin/activate

# 运行采集程序
python3 capture.py
```

采集建议：

- 每个用户采集 20-30 张照片
- 包含不同角度、光线条件
- 表情自然，眼睛看向摄像头

### 2. 训练识别模型

```bash
# 训练模型
python3 train_model.py
```

训练完成后会生成 `models/face_model.pkl` 文件。

### 3. 测试识别

```bash
# 测试识别功能
python3 run.py
# 选择单次识别或测试模式
```

## 🔧 系统服务配置

### 1. 安装为系统服务

```bash
# 确保脚本可执行
chmod +x install_service.sh service_manager.sh

# 安装服务
./install_service.sh
```

### 2. 管理系统服务

```bash
# 查看服务状态
./service_manager.sh status

# 启动服务
./service_manager.sh start

# 查看日志
./service_manager.sh logs

# 重启服务
./service_manager.sh restart

# 停止服务
./service_manager.sh stop
```

### 3. 设置开机自启

```bash
# 启用开机自启
./service_manager.sh enable

# 禁用开机自启
./service_manager.sh disable
```

## ✅ 测试验证

### 1. 基础功能测试

```bash
# 测试摄像头
rpicam-hello -t 2000

# 测试Python环境
python3 -c "import face_recognition; print('Face recognition OK')"

# 测试OpenCV
python3 -c "import cv2; print('OpenCV OK')"
```

### 2. 人脸识别测试

```bash
# 命令行测试
python3 run.py

# Web界面测试
python3 web_trigger.py
# 然后访问 http://树莓派IP:5000
```

### 3. Mac 连接测试

```bash
# 测试Mac连接
python3 utils/mac_trigger.py
```

### 4. 系统服务测试

```bash
# 检查服务状态
sudo systemctl status face-unlock-web

# 检查Web服务
curl http://localhost:5000/health
```

## 🔧 常见问题解决

### 1. 摄像头问题

**问题**：摄像头无法检测

```bash
# 检查摄像头连接
lsusb  # USB摄像头
vcgencmd get_camera  # CSI摄像头

# 重新配置摄像头
sudo raspi-config
```

**问题**：权限错误

```bash
# 添加用户到video组
sudo usermod -a -G video $USER
# 重新登录
```

### 2. face_recognition 安装问题

**问题**：编译失败

```bash
# 增加swap空间
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 重新安装
pip install face_recognition
```

**问题**：依赖缺失

```bash
# 安装系统级face_recognition
sudo apt install python3-face-recognition
```

### 3. 网络连接问题

**问题**：Mac 连接失败

- 检查防火墙设置
- 确认 IP 地址正确
- 测试端口连通性：`telnet MAC_IP 5001`

### 4. 性能问题

**问题**：识别速度慢

```bash
# 降低图像分辨率
# 在config.json中调整：
{
  "camera": {
    "width": 640,
    "height": 480
  }
}
```

**问题**：内存不足

```bash
# 增加GPU内存分配
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt
sudo reboot
```

## 🔒 安全配置

### 1. 网络安全

```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # Web服务
sudo ufw allow from 192.168.1.0/24  # 仅允许局域网访问
```

### 2. 数据安全

```bash
# 设置文件权限
chmod 600 config.json
chmod 700 faces/
chmod 700 models/

# 定期备份
tar -czf backup_$(date +%Y%m%d).tar.gz faces/ models/ config.json
```

### 3. 系统安全

```bash
# 禁用不必要的服务
sudo systemctl disable bluetooth
sudo systemctl disable cups

# 定期更新
sudo apt update && sudo apt upgrade
```

## 📊 监控和维护

### 1. 日志监控

```bash
# 查看系统日志
sudo journalctl -u face-unlock-web -f

# 查看应用日志
tail -f logs/face_unlock_*.log
```

### 2. 性能监控

```bash
# 监控系统资源
htop

# 监控温度
vcgencmd measure_temp

# 监控磁盘空间
df -h
```

### 3. 定期维护

```bash
# 清理日志
sudo journalctl --vacuum-time=7d

# 清理临时文件
sudo apt autoremove
sudo apt autoclean

# 备份重要数据
./backup.sh  # 需要创建备份脚本
```

## 🎯 高级配置

### 1. 多用户支持

编辑 config.json 添加多个用户：

```json
{
  "authorized_users": ["user1", "user2", "user3"]
}
```

为每个用户创建人脸数据目录：

```bash
mkdir -p faces/user1 faces/user2 faces/user3
```

### 2. 定时任务

```bash
# 编辑crontab
crontab -e

# 添加定时清理任务
0 2 * * * /home/pi/face_unlock_system/cleanup.sh
```

### 3. 远程访问

配置动态 DNS 和端口转发，实现远程访问：

```bash
# 安装ddclient（可选）
sudo apt install ddclient
```

## 📝 总结

完成以上步骤后，您将拥有一个完整的树莓派人脸识别解锁系统，具备以下功能：

- ✅ 高精度人脸识别
- ✅ Mac 远程解锁
- ✅ Web 控制界面
- ✅ 系统服务自启动
- ✅ 完整的日志和监控
- ✅ 安全配置

如果遇到问题，请参考故障排除部分或查看项目 Issues。
