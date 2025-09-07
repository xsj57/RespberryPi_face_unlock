#!/bin/bash
# 人脸识别Web服务安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="face-unlock-web"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  人脸识别Web服务安装脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查是否以root权限运行
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}错误：请不要以root权限运行此脚本${NC}"
    echo -e "${YELLOW}请使用: ./install_service.sh${NC}"
    exit 1
fi

# 检查必要文件
echo -e "\n${BLUE}1. 检查必要文件...${NC}"
if [ ! -f "$SCRIPT_DIR/web_trigger.py" ]; then
    echo -e "${RED}错误：找不到 web_trigger.py${NC}"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/core/main.py" ]; then
    echo -e "${RED}错误：找不到 core/main.py${NC}"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/models/face_model.pkl" ]; then
    echo -e "${YELLOW}警告：找不到训练好的模型文件 models/face_model.pkl${NC}"
    echo -e "${YELLOW}请先运行训练脚本生成模型${NC}"
fi

echo -e "${GREEN}✓ 文件检查完成${NC}"

# 创建日志目录
echo -e "\n${BLUE}2. 创建日志目录...${NC}"
mkdir -p "$SCRIPT_DIR/logs"
echo -e "${GREEN}✓ 日志目录创建完成${NC}"

# 创建systemd服务文件
echo -e "\n${BLUE}3. 创建systemd服务文件...${NC}"
SERVICE_FILE="/tmp/${SERVICE_NAME}.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Face Recognition Web Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin
Environment=PYTHONPATH=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/web_trigger.py
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=face-unlock-web

# 安全配置
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$SCRIPT_DIR/logs
ReadWritePaths=/tmp

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ 服务文件创建完成${NC}"

# 安装服务文件
echo -e "\n${BLUE}4. 安装系统服务...${NC}"
sudo cp "$SERVICE_FILE" "/etc/systemd/system/${SERVICE_NAME}.service"
sudo systemctl daemon-reload
echo -e "${GREEN}✓ 服务安装完成${NC}"

# 启用并启动服务
echo -e "\n${BLUE}5. 启用并启动服务...${NC}"
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# 等待服务启动
sleep 3

# 检查服务状态
echo -e "\n${BLUE}6. 检查服务状态...${NC}"
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✓ 服务运行正常${NC}"
    
    # 显示服务信息
    echo -e "\n${BLUE}服务信息：${NC}"
    echo -e "  服务名称：${SERVICE_NAME}"
    echo -e "  工作目录：${SCRIPT_DIR}"
    echo -e "  Web访问：http://$(hostname -I | awk '{print $1}'):5000"
    echo -e "  日志目录：${SCRIPT_DIR}/logs"
    
    echo -e "\n${BLUE}常用命令：${NC}"
    echo -e "  查看状态：${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
    echo -e "  查看日志：${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
    echo -e "  重启服务：${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
    echo -e "  停止服务：${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
    echo -e "  禁用服务：${YELLOW}sudo systemctl disable $SERVICE_NAME${NC}"
    
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo -e "\n${YELLOW}查看错误日志：${NC}"
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20
    exit 1
fi

# 清理临时文件
rm -f "$SERVICE_FILE"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}访问 http://$(hostname -I | awk '{print $1}'):5000 使用Web界面${NC}"