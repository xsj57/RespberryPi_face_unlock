# 树莓派人脸识别解锁系统

一个基于树莓派的智能人脸识别解锁系统，支持自动识别并解锁 Mac 电脑。

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/xsj57/RespberryPi_face_unlock)

- [English](README_EN.md) - 系统服务管理指南

## ✨ 特性

- 🔐 **人脸识别解锁**：使用 face_recognition 库进行高精度人脸识别
- 🖥️ **Mac 远程解锁**：支持通过网络解锁 Mac 电脑
- 🌐 **Web 控制界面**：提供友好的移动端 Web 界面
- 🔧 **系统服务**：支持开机自启和异常重启
- 📊 **实时监控**：提供详细的识别统计和日志
- 🎯 **多种触发方式**：支持手动、Web、定时等多种触发模式

## 📁 项目结构

```
face_unlock_system/
├── README.md              # 项目说明
├── DEPLOYMENT.md          # 部署指南
├── requirements.txt       # Python依赖
├── .gitignore            # Git忽略文件
├── config.template.json  # 配置模板
├── config.json           # 实际配置（需要创建）
├── run.py                # 主启动文件
├── web_trigger.py        # Web触发服务
├── capture.py            # 人脸采集工具
├── train_model.py        # 模型训练工具
├── core/                 # 核心模块
│   └── main.py          # 核心识别程序
├── utils/                # 工具模块
│   ├── mac_trigger.py   # Mac解锁工具
│   └── trigger_handler.py
├── models/               # 训练模型存储
├── faces/                # 人脸数据存储
├── logs/                 # 日志文件
├── service_manager.sh    # 服务管理脚本
├── install_service.sh    # 服务安装脚本
└── backup_old/          # 旧版本备份
```

## 🚀 快速开始

### 环境要求

- 树莓派 4/5（推荐 8GB 内存）
- 树莓派官方摄像头或 USB 摄像头
- Python 3.7+
- Mac 电脑（需要安装对应的解锁服务）

### 安装步骤

1. **克隆项目**

   ```bash
   git clone <your-repo-url>
   cd face_unlock_system
   ```

2. **安装依赖**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **配置系统**

   ```bash
   cp config.template.json config.json
   # 编辑config.json，填入您的Mac信息
   nano config.json
   ```

4. **采集人脸数据**

   ```bash
   python3 capture.py
   ```

5. **训练模型**

   ```bash
   python3 train_model.py
   ```

6. **测试运行**

   ```bash
   python3 run.py
   ```

7. **安装为系统服务**（可选）
   ```bash
   ./install_service.sh
   ```

## 📖 详细文档

- [完整部署指南](DEPLOYMENT.md) - 详细的安装和配置说明
- [服务管理文档](SERVICE_README.md) - 系统服务管理指南

## 🔧 配置说明

主要配置项：

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

## 🌐 Web 界面

启动 Web 服务后，可通过浏览器访问：

```
http://树莓派IP:5000
```

功能包括：

- 手动触发人脸识别
- 查看系统状态
- 测试 Mac 连接
- 移动端友好界面

## 🛠️ 服务管理

使用服务管理脚本：

```bash
# 启动服务
./service_manager.sh start

# 查看状态
./service_manager.sh status

# 查看日志
./service_manager.sh logs

# 重启服务
./service_manager.sh restart
```

## 📝 使用方法

### 命令行模式

```bash
python3 run.py
```

### Web 模式

````bash
python3 web_trigger.py

### 训练模型
python3 core/train_model.py
### 拍照采集
python3 core/capture.py
### 测试Mac连接
```bash
python3 utils/mac_trigger.py
````

## 🔍 故障排除

### 常见问题

1. **摄像头无法使用**

   ```bash
   # 测试摄像头
   rpicam-hello -t 2000
   ```

2. **face_recognition 安装失败**

   ```bash
   # 安装预编译版本
   sudo apt update
   sudo apt install python3-face-recognition
   ```

3. **Mac 连接失败**

   - 检查 Mac IP 地址和端口
   - 确保 Mac 上的解锁服务正在运行
   - 检查网络连接

4. **服务无法启动**
   ```bash
   # 查看详细错误
   sudo journalctl -u face-unlock-web -f
   ```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## ⚠️ 安全提醒

- 请妥善保管配置文件中的密码信息
- 建议在局域网环境中使用
- 定期更新系统和依赖包
- 不要将包含个人信息的配置文件上传到公共仓库
