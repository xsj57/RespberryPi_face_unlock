# Face Recognition Web Service - Service Management Guide

## Overview

This document provides comprehensive guidance for managing the Face Recognition Web Service as a system service.

## Service Features

- **Auto-start on boot**: Service automatically starts when the system boots
- **Automatic restart**: Service automatically restarts on failure
- **Log management**: Comprehensive logging with rotation
- **System integration**: Full systemd integration for monitoring and control

## Installation

### Prerequisites

- Raspberry Pi OS with systemd
- Python 3.7+
- Face recognition system properly configured
- Web service dependencies installed

### Quick Installation

```bash
# Make scripts executable
chmod +x install_service.sh service_manager.sh

# Install service
./install_service.sh
```

### Manual Installation

1. **Copy service file**:

   ```bash
   sudo cp face-unlock-web.service /etc/systemd/system/
   ```

2. **Reload systemd**:

   ```bash
   sudo systemctl daemon-reload
   ```

3. **Enable service**:

   ```bash
   sudo systemctl enable face-unlock-web
   ```

4. **Start service**:
   ```bash
   sudo systemctl start face-unlock-web
   ```

## Service Management

### Using service_manager.sh Script

The `service_manager.sh` script provides convenient commands for service management:

```bash
# Start service
./service_manager.sh start

# Stop service
./service_manager.sh stop

# Restart service
./service_manager.sh restart

# Check status
./service_manager.sh status

# View logs (real-time)
./service_manager.sh logs

# Enable auto-start
./service_manager.sh enable

# Disable auto-start
./service_manager.sh disable

# Uninstall service
./service_manager.sh uninstall
```

### Using systemctl Commands

You can also use standard systemctl commands:

```bash
# Start service
sudo systemctl start face-unlock-web

# Stop service
sudo systemctl stop face-unlock-web

# Restart service
sudo systemctl restart face-unlock-web

# Check status
sudo systemctl status face-unlock-web

# Enable auto-start
sudo systemctl enable face-unlock-web

# Disable auto-start
sudo systemctl disable face-unlock-web

# View logs
sudo journalctl -u face-unlock-web -f
```

## Service Configuration

### Service File Location

```
/etc/systemd/system/face-unlock-web.service
```

### Key Configuration Options

```ini
[Unit]
Description=Face Recognition Web Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/face_unlock_system
ExecStart=/usr/bin/python3 web_trigger.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Environment Variables

The service runs with the following environment:

- `PATH`: Includes system Python paths
- `PYTHONPATH`: Set to project directory
- Working directory: Project root

## Logging

### System Logs

Service logs are managed by systemd and can be viewed using:

```bash
# View recent logs
sudo journalctl -u face-unlock-web

# Follow logs in real-time
sudo journalctl -u face-unlock-web -f

# View logs since boot
sudo journalctl -u face-unlock-web -b

# View logs for specific time period
sudo journalctl -u face-unlock-web --since "2024-01-01" --until "2024-01-02"
```

### Application Logs

Application-specific logs are stored in the `logs/` directory:

- `face_unlock_YYYYMMDD.log` - Main application logs
- `events_YYYYMMDD.log` - Event logs
- `recognition_YYYYMMDD.log` - Recognition result logs

### Log Rotation

Logs are automatically rotated based on:

- Size limit: 10MB per file
- Keep count: 5 files
- Daily rotation

## Monitoring

### Health Check

The service provides a health check endpoint:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "face-unlock-web",
  "timestamp": 1640995200.0,
  "system_initialized": true,
  "is_processing": false,
  "version": "1.0"
}
```

### Service Status

Check service status:

```bash
./service_manager.sh status
```

This will show:

- Service state (running/stopped/failed)
- Uptime
- Recent log entries
- Web access URL

### System Resources

Monitor system resources:

```bash
# CPU and memory usage
htop

# Service-specific resource usage
systemctl status face-unlock-web

# Disk usage
df -h
```

## Troubleshooting

### Service Won't Start

1. **Check service status**:

   ```bash
   sudo systemctl status face-unlock-web
   ```

2. **View detailed logs**:

   ```bash
   sudo journalctl -u face-unlock-web -n 50
   ```

3. **Check file permissions**:

   ```bash
   ls -la /home/pi/face_unlock_system/
   ```

4. **Verify Python dependencies**:
   ```bash
   cd /home/pi/face_unlock_system
   python3 -c "import flask, face_recognition"
   ```

### Service Keeps Restarting

1. **Check application logs**:

   ```bash
   tail -f logs/face_unlock_*.log
   ```

2. **Test manual start**:

   ```bash
   cd /home/pi/face_unlock_system
   python3 web_trigger.py
   ```

3. **Check configuration**:
   ```bash
   cat config.json
   ```

### Web Interface Not Accessible

1. **Check service is running**:

   ```bash
   ./service_manager.sh status
   ```

2. **Test local connection**:

   ```bash
   curl http://localhost:5000/health
   ```

3. **Check firewall**:

   ```bash
   sudo ufw status
   ```

4. **Verify network configuration**:
   ```bash
   ip addr show
   ```

### Performance Issues

1. **Monitor resources**:

   ```bash
   htop
   top -p $(pgrep -f web_trigger.py)
   ```

2. **Check system load**:

   ```bash
   uptime
   cat /proc/loadavg
   ```

3. **Monitor temperature**:
   ```bash
   vcgencmd measure_temp
   ```

### Common Error Messages

**Error**: `ModuleNotFoundError: No module named 'face_recognition'`
**Solution**: Install face_recognition dependencies:

```bash
sudo apt install python3-face-recognition
```

**Error**: `Permission denied: '/dev/video0'`
**Solution**: Add user to video group:

```bash
sudo usermod -a -G video pi
```

**Error**: `Address already in use`
**Solution**: Stop existing service or change port:

```bash
sudo systemctl stop face-unlock-web
```

## Advanced Configuration

### Custom Service Configuration

To modify service configuration:

1. **Edit service file**:

   ```bash
   sudo systemctl edit face-unlock-web
   ```

2. **Reload configuration**:

   ```bash
   sudo systemctl daemon-reload
   ```

3. **Restart service**:
   ```bash
   sudo systemctl restart face-unlock-web
   ```

### Multiple Instances

To run multiple instances on different ports:

1. **Copy service file**:

   ```bash
   sudo cp /etc/systemd/system/face-unlock-web.service /etc/systemd/system/face-unlock-web-2.service
   ```

2. **Modify port and working directory**
3. **Enable and start new service**

### Security Hardening

Additional security measures:

```ini
[Service]
# Run with minimal privileges
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/pi/face_unlock_system/logs

# Network restrictions
RestrictAddressFamilies=AF_INET AF_INET6
```

## Backup and Recovery

### Service Configuration Backup

```bash
# Backup service file
sudo cp /etc/systemd/system/face-unlock-web.service /path/to/backup/

# Backup application configuration
./backup.sh
```

### Service Recovery

```bash
# Restore service file
sudo cp /path/to/backup/face-unlock-web.service /etc/systemd/system/

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl enable face-unlock-web
sudo systemctl start face-unlock-web
```

## Maintenance

### Regular Tasks

1. **Check service status** (weekly):

   ```bash
   ./service_manager.sh status
   ```

2. **Clean old logs** (monthly):

   ```bash
   sudo journalctl --vacuum-time=30d
   ```

3. **Update system** (monthly):

   ```bash
   sudo apt update && sudo apt upgrade
   ```

4. **Backup configuration** (monthly):
   ```bash
   ./backup.sh
   ```

### Performance Optimization

1. **Adjust log levels** in config.json
2. **Configure log rotation** settings
3. **Monitor resource usage** regularly
4. **Update dependencies** as needed

## Support

For additional support:

1. Check the main [README](README_EN.md)
2. Review [Deployment Guide](DEPLOYMENT_EN.md)
3. Submit issues on GitHub
4. Check system logs for detailed error information

---

This service management system ensures reliable operation of your face recognition unlock system with minimal maintenance requirements.
