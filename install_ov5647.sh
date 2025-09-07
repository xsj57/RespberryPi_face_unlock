#!/bin/bash

echo "=== OV5647摄像头环境配置 ==="

# 1. 更新系统
echo "更新系统..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. 安装摄像头相关工具
echo "安装摄像头工具..."
sudo apt-get install -y libcamera-apps libcamera-tools
sudo apt-get install -y v4l-utils

# 3. 配置摄像头
echo "配置摄像头..."
sudo bash -c 'cat >> /boot/firmware/config.txt << EOF

# OV5647 Camera Configuration
camera_auto_detect=1
dtoverlay=ov5647
gpu_mem=128
start_x=1

EOF'

# 4. 设置权限
echo "设置权限..."
sudo usermod -a -G video $USER

# 5. 安装Python依赖
echo "安装Python依赖..."
pip install opencv-python
pip install numpy
pip install picamera2  # 可选，用于更好的摄像头控制

echo "配置完成！请重启系统：sudo reboot"
