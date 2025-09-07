# 🔐 Raspberry Pi Face Recognition Unlock System

[中文](README.md) 

An intelligent face recognition unlock system based on Raspberry Pi that supports automatic recognition and unlocking of Mac computers.

## ✨ Features

- 🔒 **Face Recognition Unlock**: High-precision face recognition using face_recognition library
- 🖥️ **Mac Remote Unlock**: Support for unlocking Mac computers via network
- 🌐 **Web Control Interface**: User-friendly mobile web interface
- 🔧 **System Service**: Support for auto-start on boot and automatic restart on failure
- 📊 **Real-time Monitoring**: Detailed recognition statistics and logging
- 🎯 **Multiple Trigger Modes**: Support for manual, web, scheduled and other trigger modes

## 📁 Project Structure

```
face_unlock_system/
├── README.md              # Project documentation
├── README_EN.md           # English documentation
├── DEPLOYMENT.md          # Deployment guide
├── DEPLOYMENT_EN.md       # English deployment guide
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
├── config.template.json  # Configuration template
├── config.json           # Actual configuration (needs to be created)
├── run.py                # Main startup file
├── web_trigger.py        # Web trigger service
├── capture.py            # Face capture tool
├── train_model.py        # Model training tool
├── core/                 # Core modules
│   └── main.py          # Core recognition program
├── utils/                # Utility modules
│   ├── mac_trigger.py   # Mac unlock tool
│   └── trigger_handler.py
├── models/               # Trained model storage
├── faces/                # Face data storage
├── logs/                 # Log files
├── service_manager.sh    # Service management script
├── install_service.sh    # Service installation script
└── backup_old/          # Old version backup
```

## 🚀 Quick Start

### Environment Requirements

- Raspberry Pi 4/5 (8GB RAM recommended)
- Raspberry Pi official camera or USB camera
- Python 3.7+
- Mac computer (requires corresponding unlock service installation)

### Installation Steps

1. **Clone Project**

   ```bash
   git clone <your-repo-url>
   cd face_unlock_system
   ```

2. **Install Dependencies**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure System**

   ```bash
   cp config.template.json config.json
   # Edit config.json and fill in your Mac information
   nano config.json
   ```

4. **Collect Face Data**

   ```bash
   python3 capture.py
   ```

5. **Train Model**

   ```bash
   python3 train_model.py
   ```

6. **Test Run**

   ```bash
   python3 run.py
   ```

7. **Install as System Service** (Optional)
   ```bash
   ./install_service.sh
   ```

## 📖 Detailed Documentation

- [Complete Deployment Guide](DEPLOYMENT_EN.md) - Detailed installation and configuration instructions
- [Service Management Documentation](SERVICE_README_EN.md) - System service management guide

## 🔧 Configuration

Main configuration items:

```json
{
  "mac": {
    "enabled": true,
    "host": "YOUR_MAC_IP_OR_HOSTNAME",
    "username": "YOUR_MAC_USERNAME",
    "password": "YOUR_MAC_PASSWORD"
  },
  "authorized_users": ["user1"],
  "web": {
    "enabled": true,
    "port": 5000
  }
}
```

## 🌐 Web Interface

After starting the web service, access via browser:

```
http://RaspberryPi_IP:5000
```

Features include:

- Manual trigger face recognition
- View system status
- Test Mac connection
- Mobile-friendly interface

## 🛠️ Service Management

Using service management script:

```bash
# Start service
./service_manager.sh start

# View status
./service_manager.sh status

# View logs
./service_manager.sh logs

# Restart service
./service_manager.sh restart
```

## 📝 Usage Methods

### Command Line Mode

```bash
python3 run.py
```

### Web Mode

```bash
python3 web_trigger.py
```

### Test Mac Connection

```bash
python3 utils/mac_trigger.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Camera Not Working**

   ```bash
   # Test camera
   rpicam-hello -t 2000
   ```

2. **face_recognition Installation Failed**

   ```bash
   # Install precompiled version
   sudo apt update
   sudo apt install python3-face-recognition
   ```

3. **Mac Connection Failed**

   - Check Mac IP address and port
   - Ensure Mac unlock service is running
   - Check network connectivity

4. **Service Cannot Start**
   ```bash
   # View detailed errors
   sudo journalctl -u face-unlock-web -f
   ```

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Security Reminders

- Please properly protect password information in configuration files
- Recommended for use in local network environments
- Regularly update system and dependency packages
- Do not upload configuration files containing personal information to public repositories
