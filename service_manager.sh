#!/bin/bash
# 人脸识别Web服务管理脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="face-unlock-web"

show_help() {
    echo -e "${BLUE}人脸识别Web服务管理工具${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo -e "  ${GREEN}start${NC}     启动服务"
    echo -e "  ${GREEN}stop${NC}      停止服务"
    echo -e "  ${GREEN}restart${NC}   重启服务"
    echo -e "  ${GREEN}status${NC}    查看服务状态"
    echo -e "  ${GREEN}logs${NC}      查看实时日志"
    echo -e "  ${GREEN}enable${NC}    启用开机自启"
    echo -e "  ${GREEN}disable${NC}   禁用开机自启"
    echo -e "  ${GREEN}install${NC}   安装服务"
    echo -e "  ${GREEN}uninstall${NC} 卸载服务"
    echo -e "  ${GREEN}help${NC}      显示此帮助"
    echo ""
}

check_service_exists() {
    if ! systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
        echo -e "${RED}错误：服务 ${SERVICE_NAME} 未安装${NC}"
        echo -e "${YELLOW}请先运行: $0 install${NC}"
        exit 1
    fi
}

case "$1" in
    "start")
        check_service_exists
        echo -e "${BLUE}启动服务...${NC}"
        sudo systemctl start "$SERVICE_NAME"
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ 服务启动成功${NC}"
            IP=$(hostname -I | awk '{print $1}')
            echo -e "${YELLOW}Web访问地址: http://${IP}:5000${NC}"
        else
            echo -e "${RED}✗ 服务启动失败${NC}"
            sudo systemctl status "$SERVICE_NAME" --no-pager -l
        fi
        ;;
        
    "stop")
        check_service_exists
        echo -e "${BLUE}停止服务...${NC}"
        sudo systemctl stop "$SERVICE_NAME"
        echo -e "${GREEN}✓ 服务已停止${NC}"
        ;;
        
    "restart")
        check_service_exists
        echo -e "${BLUE}重启服务...${NC}"
        sudo systemctl restart "$SERVICE_NAME"
        sleep 2
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ 服务重启成功${NC}"
        else
            echo -e "${RED}✗ 服务重启失败${NC}"
            sudo systemctl status "$SERVICE_NAME" --no-pager -l
        fi
        ;;
        
    "status")
        check_service_exists
        echo -e "${BLUE}服务状态：${NC}"
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        echo ""
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            IP=$(hostname -I | awk '{print $1}')
            echo -e "${GREEN}✓ 服务运行中${NC}"
            echo -e "${YELLOW}Web访问地址: http://${IP}:5000${NC}"
        else
            echo -e "${RED}✗ 服务未运行${NC}"
        fi
        ;;
        
    "logs")
        check_service_exists
        echo -e "${BLUE}实时日志 (按Ctrl+C退出)：${NC}"
        sudo journalctl -u "$SERVICE_NAME" -f
        ;;
        
    "enable")
        check_service_exists
        echo -e "${BLUE}启用开机自启...${NC}"
        sudo systemctl enable "$SERVICE_NAME"
        echo -e "${GREEN}✓ 开机自启已启用${NC}"
        ;;
        
    "disable")
        check_service_exists
        echo -e "${BLUE}禁用开机自启...${NC}"
        sudo systemctl disable "$SERVICE_NAME"
        echo -e "${GREEN}✓ 开机自启已禁用${NC}"
        ;;
        
    "install")
        if [ ! -f "./install_service.sh" ]; then
            echo -e "${RED}错误：找不到安装脚本 install_service.sh${NC}"
            exit 1
        fi
        ./install_service.sh
        ;;
        
    "uninstall")
        echo -e "${YELLOW}确定要卸载服务吗？(y/N): ${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}卸载服务...${NC}"
            
            # 停止并禁用服务
            if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
                sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
                sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
                sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
                sudo systemctl daemon-reload
            fi
            
            echo -e "${GREEN}✓ 服务已卸载${NC}"
        else
            echo -e "${YELLOW}取消卸载${NC}"
        fi
        ;;
        
    "help"|"--help"|"-h"|"")
        show_help
        ;;
        
    *)
        echo -e "${RED}错误：未知命令 '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac