# 🚀 树莓派人脸识别解锁系统 - 快速部署指南

## 📋 部署流程概述

本指南提供从零开始在树莓派上部署人脸识别解锁系统的完整流程。

## 🔧 第一步：环境准备

### 硬件要求

- 树莓派 4B/5（推荐 8GB 内存）
- 树莓派摄像头模块或 USB 摄像头
- MicroSD 卡（32GB 以上）
- 稳定的网络连接

### 软件要求

- Raspberry Pi OS（最新版本）
- Python 3.7+
- 网络连接的 Mac 电脑

## 🏗️ 第二步：系统配置

### 1. 更新系统

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv
```

### 2. 启用摄像头

```bash
sudo raspi-config
# Interface Options -> Camera -> Enable
sudo reboot
```

### 3. 测试摄像头

```bash
rpicam-hello -t 2000
```

## 📦 第三步：部署项目

### 1. 克隆项目

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/face_unlock_system.git
cd face_unlock_system
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 如果face_recognition安装失败，使用系统包
sudo apt install python3-face-recognition
```

### 3. 配置系统

```bash
# 复制配置模板
cp config.template.json config.json

# 编辑配置文件
nano config.json
```

**重要配置项：**

```json
{
  "mac": {
    "enabled": true,
    "host": "你的Mac的IP地址",
    "username": "你的Mac用户名",
    "password": "你的Mac密码"
  },
  "authorized_users": ["你的用户名"]
}
```

## 👤 第四步：人脸数据准备

### 1. 采集人脸数据

```bash
python3 capture.py
# 按提示输入用户名，采集20-30张照片
```

### 2. 训练模型

```bash
python3 train_model.py
```

### 3. 测试识别

```bash
python3 run.py
# 选择单次识别测试
```

## 🍎 第五步：Mac 端配置

### 1. 创建解锁服务

在 Mac 上创建文件 `mac_unlock_service.py`：

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
            # 这里实现解锁逻辑
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "你的密码"'])
            return jsonify({'status': 'success'})
        except:
            return jsonify({'status': 'error'}), 500
    return jsonify({'status': 'unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### 2. 运行 Mac 服务

```bash
pip3 install flask
python3 mac_unlock_service.py
```

## 🔧 第六步：系统服务化

### 1. 安装为系统服务

```bash
./install_service.sh
```

### 2. 管理服务

```bash
# 查看状态
./service_manager.sh status

# 启动服务
./service_manager.sh start

# 查看日志
./service_manager.sh logs
```

## 🌐 第七步：Web 界面访问

服务启动后，通过浏览器访问：

```
http://树莓派IP地址:5000
```

功能包括：

- 手动触发人脸识别
- 查看系统状态
- 测试 Mac 连接

## ✅ 第八步：验证部署

### 1. 功能测试

- [ ] 摄像头正常工作
- [ ] 人脸识别准确
- [ ] Mac 解锁成功
- [ ] Web 界面可访问
- [ ] 系统服务自启动

### 2. 性能测试

```bash
# 检查识别速度
python3 run.py

# 检查系统资源
htop
```

## 🔒 第九步：安全配置

### 1. 网络安全

```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 5000
sudo ufw allow from 192.168.1.0/24
```

### 2. 数据安全

```bash
# 设置文件权限
chmod 600 config.json
chmod 700 faces/ models/
```

## 📊 第十步：监控维护

### 1. 日志监控

```bash
# 查看系统日志
sudo journalctl -u face-unlock-web -f

# 查看应用日志
tail -f logs/face_unlock_*.log
```

### 2. 备份数据

```bash
# 运行备份脚本
./backup.sh
```

## 🚨 故障排除

### 常见问题

1. **摄像头无法工作**

   ```bash
   sudo raspi-config  # 重新启用摄像头
   ```

2. **face_recognition 安装失败**

   ```bash
   sudo apt install python3-face-recognition
   ```

3. **Mac 连接失败**

   - 检查 IP 地址和端口
   - 确认 Mac 服务运行
   - 测试网络连通性

4. **Web 服务无法访问**
   ```bash
   sudo systemctl status face-unlock-web
   ```

## ⚡ 快速命令参考

```bash
# 项目管理
./service_manager.sh start     # 启动服务
./service_manager.sh stop      # 停止服务
./service_manager.sh status    # 查看状态
./service_manager.sh logs      # 查看日志

# 系统维护
./backup.sh                    # 备份数据
./pre_upload_check.sh         # 安全检查

# 功能测试
python3 run.py                # 命令行测试
python3 web_trigger.py        # Web服务测试
python3 utils/mac_trigger.py  # Mac连接测试
```

## 📞 获取帮助

- 查看 [完整部署指南](DEPLOYMENT.md)
- 查看 [服务管理文档](SERVICE_README.md)
- 提交 [GitHub Issues](https://github.com/YOUR_USERNAME/face_unlock_system/issues)

---

**部署完成后，您将拥有一个功能完整的人脸识别解锁系统！**
