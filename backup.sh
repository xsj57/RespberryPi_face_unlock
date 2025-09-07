#!/bin/bash
# 人脸识别系统备份脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="face_unlock_backup_$TIMESTAMP.tar.gz"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  人脸识别系统备份工具${NC}"
echo -e "${GREEN}========================================${NC}"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo -e "\n${YELLOW}开始备份...${NC}"

# 要备份的文件和目录
BACKUP_ITEMS=(
    "config.json"
    "faces/"
    "models/"
    "logs/"
    "requirements.txt"
    "*.py"
    "*.sh"
    "*.md"
)

# 创建临时目录
TEMP_DIR="/tmp/face_unlock_backup_$TIMESTAMP"
mkdir -p "$TEMP_DIR"

echo "备份以下项目："

# 复制文件到临时目录
for item in "${BACKUP_ITEMS[@]}"; do
    if ls $item 1> /dev/null 2>&1; then
        echo "  - $item"
        cp -r $item "$TEMP_DIR/"
    fi
done

# 创建备份信息文件
cat > "$TEMP_DIR/backup_info.txt" << EOF
备份时间: $(date)
备份主机: $(hostname)
系统版本: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
Python版本: $(python3 --version)
备份内容: ${BACKUP_ITEMS[*]}
EOF

# 创建压缩包
cd /tmp
tar -czf "$BACKUP_DIR/$BACKUP_FILE" "face_unlock_backup_$TIMESTAMP/"

# 清理临时目录
rm -rf "$TEMP_DIR"

# 显示结果
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
echo -e "\n${GREEN}✓ 备份完成！${NC}"
echo -e "备份文件: $BACKUP_DIR/$BACKUP_FILE"
echo -e "文件大小: $BACKUP_SIZE"

# 清理旧备份（保留最近7个）
echo -e "\n${YELLOW}清理旧备份文件...${NC}"
cd "$BACKUP_DIR"
ls -t face_unlock_backup_*.tar.gz | tail -n +8 | xargs -r rm -f
REMAINING=$(ls face_unlock_backup_*.tar.gz 2>/dev/null | wc -l)
echo -e "保留最近 $REMAINING 个备份文件"

echo -e "\n${GREEN}备份任务完成！${NC}"
echo -e "\n${YELLOW}恢复方法：${NC}"
echo -e "1. 解压备份文件："
echo -e "   tar -xzf $BACKUP_FILE"
echo -e "2. 复制文件到系统目录："
echo -e "   cp -r face_unlock_backup_$TIMESTAMP/* /path/to/face_unlock_system/"