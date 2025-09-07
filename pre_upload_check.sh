#!/bin/bash
# GitHub上传前检查脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GitHub 上传前安全检查${NC}"
echo -e "${BLUE}========================================${NC}"

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查函数
check_passed=0
check_failed=0

check_item() {
    local description="$1"
    local condition="$2"
    
    echo -n "检查 $description... "
    
    if eval "$condition"; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((check_passed++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((check_failed++))
        return 1
    fi
}

echo -e "\n${YELLOW}开始安全检查...${NC}\n"

# 1. 检查是否存在个人敏感信息
echo -e "${BLUE}1. 检查敏感信息${NC}"
check_item "配置文件中是否包含真实密码" '! grep -r "Xsj507001\|McDouble\|ericxu" . --exclude-dir=.git --exclude="*.md" --exclude="pre_upload_check.sh" || true'
check_item "是否移除了个人人脸数据" '[ ! -d "faces/ericxu" ]'
check_item "是否清理了个人日志" '[ $(find logs/ -name "*.log" 2>/dev/null | wc -l) -eq 0 ]'

# 2. 检查必要文件
echo -e "\n${BLUE}2. 检查必要文件${NC}"
check_item ".gitignore文件存在" '[ -f ".gitignore" ]'
check_item "requirements.txt文件存在" '[ -f "requirements.txt" ]'
check_item "配置模板文件存在" '[ -f "config.template.json" ]'
check_item "部署指南存在" '[ -f "DEPLOYMENT.md" ]'
check_item "README文件完整" '[ -f "README.md" ] && [ $(wc -l < README.md) -gt 50 ]'

# 3. 检查代码质量
echo -e "\n${BLUE}3. 检查代码质量${NC}"
check_item "Python语法检查" 'python3 -m py_compile core/main.py web_trigger.py train_model.py capture.py'
check_item "Shell脚本语法检查" 'bash -n service_manager.sh install_service.sh backup.sh'

# 4. 检查Git状态
echo -e "\n${BLUE}4. 检查Git状态${NC}"
if [ -d ".git" ]; then
    check_item "Git仓库已初始化" 'true'
    check_item "没有未提交的敏感文件" '! git status --porcelain | grep -E "(config\.json|faces/.*|models/.*\.pkl|logs/.*\.log)" || true'
else
    echo -e "${YELLOW}Git仓库未初始化，跳过Git检查${NC}"
fi

# 5. 检查文件权限
echo -e "\n${BLUE}5. 检查文件权限${NC}"
check_item "脚本文件可执行" '[ -x "service_manager.sh" ] && [ -x "install_service.sh" ] && [ -x "backup.sh" ]'

# 显示结果
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  检查结果${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $check_failed -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过 ($check_passed/$((check_passed + check_failed)))${NC}"
    echo -e "${GREEN}项目已准备好上传到GitHub！${NC}"
    
    echo -e "\n${YELLOW}建议的Git命令：${NC}"
    echo -e "git add ."
    echo -e "git commit -m \"Initial commit: Raspberry Pi Face Recognition Unlock System\""
    echo -e "git push origin main"
    
else
    echo -e "${RED}✗ 检查失败 ($check_failed 项)，通过 ($check_passed 项)${NC}"
    echo -e "${RED}请修复上述问题后再上传到GitHub${NC}"
    exit 1
fi

echo -e "\n${YELLOW}注意事项：${NC}"
echo -e "1. 确保不要上传包含真实密码的config.json文件"
echo -e "2. 用户需要根据config.template.json创建自己的配置"
echo -e "3. 建议在README.md中添加安全使用说明"
echo -e "4. 考虑添加LICENSE文件"

echo -e "\n${GREEN}检查完成！${NC}"