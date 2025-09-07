# 🚀 Raspberry Pi Face Recognition Unlock System - Quick Deployment Guide

## 📋 Deployment Process Overview

This guide provides the complete process for deploying the face recognition unlock system on Raspberry Pi from scratch.

## 🔧 Step 1: Environment Preparation

### Hardware Requirements

- Raspberry Pi 4B/5 (8GB RAM recommended)
- Raspberry Pi camera module or USB camera
- MicroSD card (32GB+)
- Stable network connection

### Software Requirements

- Raspberry Pi OS (latest version)
- Python 3.7+
- Network-connected Mac computer

## 🏗️ Step 2: System Configuration

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv
```

### 2. Enable Camera

```bash
sudo raspi-config
# Interface Options -> Camera -> Enable
sudo reboot
```

### 3. Test Camera

```bash
rpicam-hello -t 2000
```

## 📦 Step 3: Deploy Project

### 1. Clone Project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/face_unlock_system.git
cd face_unlock_system
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# If face_recognition installation fails, use system package
sudo apt install python3-face-recognition
```

### 3. Configure System

```bash
# Copy configuration template
cp config.template.json config.json

# Edit configuration file
nano config.json
```

**Important configuration items:**

```json
{
  "mac": {
    "enabled": true,
    "host": "YOUR_MAC_IP_ADDRESS",
    "username": "YOUR_MAC_USERNAME",
    "password": "YOUR_MAC_PASSWORD"
  },
  "authorized_users": ["your_username"]
}
```

## 👤 Step 4: Face Data Preparation

### 1. Collect Face Data

```bash
python3 capture.py
# Follow prompts to enter username, collect 20-30 photos
```

### 2. Train Model

```bash
python3 train_model.py
```

### 3. Test Recognition

```bash
python3 run.py
# Choose single recognition test
```

## 🍎 Step 5: Mac Configuration

### 1. Create Unlock Service

Create file `mac_unlock_service.py` on Mac:

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/status')
def status():
    return jsonify({'status': 'running'})

@app.route('/unlock', methods=['POST'])
def unlock():
    data = request.get_json()
    if data.get('key') == 'face_unlock_2024':
        try:
            # Implement unlock logic here
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "your_password"'])
            return jsonify({'status': 'success'})
        except:
            return jsonify({'status': 'error'}), 500
    return jsonify({'status': 'unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### 2. Run Mac Service

```bash
pip3 install flask
python3 mac_unlock_service.py
```

## 🔧 Step 6: System Service

### 1. Install as System Service

```bash
./install_service.sh
```

### 2. Manage Service

```bash
# View status
./service_manager.sh status

# Start service
./service_manager.sh start

# View logs
./service_manager.sh logs
```

## 🌐 Step 7: Web Interface Access

After service starts, access via browser:

```
http://RaspberryPi_IP_Address:5000
```

Features include:

- Manual trigger face recognition
- View system status
- Test Mac connection

## ✅ Step 8: Validate Deployment

### 1. Function Tests

- [ ] Camera working normally
- [ ] Face recognition accurate
- [ ] Mac unlock successful
- [ ] Web interface accessible
- [ ] System service auto-start

### 2. Performance Tests

```bash
# Check recognition speed
python3 run.py

# Check system resources
htop
```

## 🔒 Step 9: Security Configuration

### 1. Network Security

```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 5000
sudo ufw allow from 192.168.1.0/24
```

### 2. Data Security

```bash
# Set file permissions
chmod 600 config.json
chmod 700 faces/ models/
```

## 📊 Step 10: Monitoring and Maintenance

### 1. Log Monitoring

```bash
# View system logs
sudo journalctl -u face-unlock-web -f

# View application logs
tail -f logs/face_unlock_*.log
```

### 2. Data Backup

```bash
# Run backup script
./backup.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Camera not working**

   ```bash
   sudo raspi-config  # Re-enable camera
   ```

2. **face_recognition installation failed**

   ```bash
   sudo apt install python3-face-recognition
   ```

3. **Mac connection failed**

   - Check IP address and port
   - Confirm Mac service running
   - Test network connectivity

4. **Web service inaccessible**
   ```bash
   sudo systemctl status face-unlock-web
   ```

## ⚡ Quick Command Reference

```bash
# Project management
./service_manager.sh start     # Start service
./service_manager.sh stop      # Stop service
./service_manager.sh status    # View status
./service_manager.sh logs      # View logs

# System maintenance
./backup.sh                    # Backup data
./pre_upload_check.sh         # Security check

# Function tests
python3 run.py                # Command line test
python3 web_trigger.py        # Web service test
python3 utils/mac_trigger.py  # Mac connection test
```

## 📞 Get Help

- View [Complete Deployment Guide](DEPLOYMENT_EN.md)
- View [Service Management Documentation](SERVICE_README.md)
- Submit [GitHub Issues](https://github.com/YOUR_USERNAME/face_unlock_system/issues)

---

**After deployment is complete, you will have a fully functional face recognition unlock system!**
