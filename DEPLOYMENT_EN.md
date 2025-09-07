# 🚀 Raspberry Pi Face Recognition Unlock System - Complete Deployment Guide

This guide provides detailed instructions for deploying the face recognition unlock system on Raspberry Pi from scratch.

## 📋 Table of Contents

1. [Hardware Preparation](#-hardware-preparation)
2. [System Environment Configuration](#-system-environment-configuration)
3. [Project Deployment](#-project-deployment)
4. [Mac Configuration](#-mac-configuration)
5. [System Service Configuration](#-system-service-configuration)
6. [Testing and Validation](#-testing-and-validation)
7. [Troubleshooting](#-troubleshooting)
8. [Security Configuration](#-security-configuration)

## 🛠 Hardware Preparation

### Required Hardware

- **Raspberry Pi 4B/5** (8GB RAM recommended)
- **MicroSD Card** (32GB+, Class 10)
- **Raspberry Pi Camera**
  - Official Camera Module V2/V3
  - Or USB Camera (UVC supported)
- **Power Adapter** (5V 3A)
- **Network Connection** (WiFi or Ethernet)

### Optional Hardware

- **Case** (with camera mount bracket)
- **Heat Sink/Fan** (for performance improvement)
- **LED Indicators** (GPIO connected, status indication)

## 💻 System Environment Configuration

### 1. Install Raspberry Pi OS

Use Raspberry Pi Imager to install the latest Raspberry Pi OS (Lite version recommended):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic tools
sudo apt install -y git vim curl wget htop
```

### 2. Enable Camera

```bash
# Method 1: Using raspi-config
sudo raspi-config
# Select Interface Options -> Camera -> Enable

# Method 2: Edit configuration file
echo 'camera_auto_detect=1' | sudo tee -a /boot/config.txt
echo 'dtoverlay=ov5647' | sudo tee -a /boot/config.txt

# Reboot system
sudo reboot
```

### 3. Install Python Environment

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install compilation tools (required for face_recognition)
sudo apt install -y build-essential cmake pkg-config

# Install OpenCV dependencies
sudo apt install -y libopencv-dev python3-opencv

# Install image processing libraries
sudo apt install -y libjpeg-dev libtiff5-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev

# Install math libraries
sudo apt install -y libatlas-base-dev gfortran
```

### 4. Install rpicam Tools

```bash
# Install latest rpicam tools
sudo apt install -y rpicam-apps

# Test camera
rpicam-hello -t 2000
```

## 📦 Project Deployment

### 1. Clone Project

```bash
# Clone project to user directory
cd ~
git clone <your-github-repo-url> face_unlock_system
cd face_unlock_system
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# If face_recognition installation fails, try precompiled version
sudo apt install -y python3-face-recognition
# Then create link in virtual environment
ln -s /usr/lib/python3/dist-packages/face_recognition venv/lib/python3.*/site-packages/
```

### 4. Configure System

```bash
# Copy configuration template
cp config.template.json config.json

# Edit configuration file
nano config.json
```

Key configuration items:

```json
{
  "mac": {
    "enabled": true,
    "host": "YOUR_MAC_IP_OR_HOSTNAME",
    "port": 5001,
    "username": "YOUR_MAC_USERNAME",
    "password": "YOUR_MAC_PASSWORD"
  },
  "authorized_users": ["your_username"],
  "web": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 5000
  }
}
```

### 5. Create Necessary Directories

```bash
# Create data directories
mkdir -p faces models logs

# Set permissions
chmod 755 faces models logs
```

## 🍎 Mac Configuration

### 1. Download Mac Unlock Service

Create unlock service script on Mac:

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
            # Simulate keyboard input to unlock password
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "your_password"'])
            return jsonify({'status': 'success', 'message': 'Mac unlocked'})
        except:
            return jsonify({'status': 'error', 'message': 'Unlock failed'}), 500
    return jsonify({'status': 'unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### 2. Install Mac Dependencies

```bash
# Install Flask on Mac
pip3 install flask

# Run unlock service
python3 mac_unlock_service.py
```

### 3. Set Mac Auto-start

Create plist file:

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

Load service:

```bash
launchctl load ~/Library/LaunchAgents/com.faceunlock.mac.plist
```

## 👤 Face Data Collection and Training

### 1. Collect Face Data

```bash
# Ensure in project directory and virtual environment
cd ~/face_unlock_system
source venv/bin/activate

# Run collection program
python3 capture.py
```

Collection recommendations:

- Collect 20-30 photos per user
- Include different angles and lighting conditions
- Natural expression, eyes looking at camera

### 2. Train Recognition Model

```bash
# Train model
python3 train_model.py
```

After training completes, `models/face_model.pkl` file will be generated.

### 3. Test Recognition

```bash
# Test recognition function
python3 run.py
# Choose single recognition or test mode
```

## 🔧 System Service Configuration

### 1. Install as System Service

```bash
# Ensure scripts are executable
chmod +x install_service.sh service_manager.sh

# Install service
./install_service.sh
```

### 2. Manage System Service

```bash
# View service status
./service_manager.sh status

# Start service
./service_manager.sh start

# View logs
./service_manager.sh logs

# Restart service
./service_manager.sh restart

# Stop service
./service_manager.sh stop
```

### 3. Set Auto-start on Boot

```bash
# Enable auto-start
./service_manager.sh enable

# Disable auto-start
./service_manager.sh disable
```

## ✅ Testing and Validation

### 1. Basic Function Tests

```bash
# Test camera
rpicam-hello -t 2000

# Test Python environment
python3 -c "import face_recognition; print('Face recognition OK')"

# Test OpenCV
python3 -c "import cv2; print('OpenCV OK')"
```

### 2. Face Recognition Tests

```bash
# Command line test
python3 run.py

# Web interface test
python3 web_trigger.py
# Then visit http://RaspberryPi_IP:5000
```

### 3. Mac Connection Test

```bash
# Test Mac connection
python3 utils/mac_trigger.py
```

### 4. System Service Test

```bash
# Check service status
sudo systemctl status face-unlock-web

# Check web service
curl http://localhost:5000/health
```

## 🔧 Troubleshooting

### 1. Camera Issues

**Problem**: Camera not detected

```bash
# Check camera connection
lsusb  # USB camera
vcgencmd get_camera  # CSI camera

# Reconfigure camera
sudo raspi-config
```

**Problem**: Permission error

```bash
# Add user to video group
sudo usermod -a -G video $USER
# Re-login
```

### 2. face_recognition Installation Issues

**Problem**: Compilation failed

```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Reinstall
pip install face_recognition
```

**Problem**: Missing dependencies

```bash
# Install system-level face_recognition
sudo apt install python3-face-recognition
```

### 3. Network Connection Issues

**Problem**: Mac connection failed

- Check firewall settings
- Confirm IP address is correct
- Test port connectivity: `telnet MAC_IP 5001`

### 4. Performance Issues

**Problem**: Slow recognition

```bash
# Lower image resolution
# Adjust in config.json:
{
  "camera": {
    "width": 640,
    "height": 480
  }
}
```

**Problem**: Insufficient memory

```bash
# Increase GPU memory allocation
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt
sudo reboot
```

## 🔒 Security Configuration

### 1. Network Security

```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # Web service
sudo ufw allow from 192.168.1.0/24  # Allow LAN only
```

### 2. Data Security

```bash
# Set file permissions
chmod 600 config.json
chmod 700 faces/
chmod 700 models/

# Regular backup
tar -czf backup_$(date +%Y%m%d).tar.gz faces/ models/ config.json
```

### 3. System Security

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups

# Regular updates
sudo apt update && sudo apt upgrade
```

## 📊 Monitoring and Maintenance

### 1. Log Monitoring

```bash
# View system logs
sudo journalctl -u face-unlock-web -f

# View application logs
tail -f logs/face_unlock_*.log
```

### 2. Performance Monitoring

```bash
# Monitor system resources
htop

# Monitor temperature
vcgencmd measure_temp

# Monitor disk space
df -h
```

### 3. Regular Maintenance

```bash
# Clean logs
sudo journalctl --vacuum-time=7d

# Clean temporary files
sudo apt autoremove
sudo apt autoclean

# Backup important data
./backup.sh  # Need to create backup script
```

## 🎯 Advanced Configuration

### 1. Multi-user Support

Edit config.json to add multiple users:

```json
{
  "authorized_users": ["user1", "user2", "user3"]
}
```

Create face data directories for each user:

```bash
mkdir -p faces/user1 faces/user2 faces/user3
```

### 2. Scheduled Tasks

```bash
# Edit crontab
crontab -e

# Add scheduled cleanup task
0 2 * * * /home/pi/face_unlock_system/cleanup.sh
```

### 3. Remote Access

Configure dynamic DNS and port forwarding for remote access:

```bash
# Install ddclient (optional)
sudo apt install ddclient
```

## 📝 Summary

After completing the above steps, you will have a complete Raspberry Pi face recognition unlock system with the following features:

- ✅ High-precision face recognition
- ✅ Mac remote unlock
- ✅ Web control interface
- ✅ System service auto-start
- ✅ Complete logging and monitoring
- ✅ Security configuration

If you encounter problems, please refer to the troubleshooting section or check project Issues.
