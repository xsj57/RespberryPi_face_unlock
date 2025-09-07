#!/bin/bash

echo "=== 整理face_unlock_system文件夹 ==="
echo

# 创建备份
echo "1. 创建备份..."
mkdir -p backup_old
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="backup_old/backup_$timestamp"
mkdir -p "$backup_dir"

# 备份可能需要的文件
files_to_backup=(
    "mac_unlocker.py"
    "mac_unlocker_v2.py"
    "main_simple.py"
    "main.py"
    "face_capture_optimized.py.old"
    "xxx-setup_training.py"
    "test_ov5647.py"
    "test_recognition.py"
    "mac_unlock_working.py"
    "face_recognition_module.py"
)

for file in "${files_to_backup[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$backup_dir/" 2>/dev/null
        echo "  备份: $file"
    fi
done

# 删除旧文件
echo
echo "2. 删除冗余文件..."
rm -f mac_unlocker.py
rm -f mac_unlocker_v2.py
rm -f main_simple.py
rm -f main.py
rm -f face_capture_optimized.py.old
rm -f xxx-setup_training.py
rm -f test_ov5647.py
rm -f test_recognition.py
rm -f mac_unlock_working.py
rm -f face_recognition_module.py
rm -f check_dependencies.py
rm -f quick_capture.py
rm -f face_capture_optimized.py
rm -f haarcascade_frontalface_default.xml
rm -f access_log.json

# 重命名保留的文件
echo
echo "3. 整理核心文件..."

# 创建清晰的目录结构
mkdir -p core
mkdir -p utils
mkdir -p tests

# 移动核心文件
mv main_final.py core/main.py 2>/dev/null
mv train_model.py core/ 2>/dev/null
mv capture_final.py core/capture.py 2>/dev/null

# 移动工具文件
mv mac_trigger_final.py utils/mac_trigger.py 2>/dev/null
mv mac_trigger.py backup_old/ 2>/dev/null
mv trigger_handler.py utils/ 2>/dev/null

# 在根目录创建主启动文件
cat > run.py << 'EOF'
#!/usr/bin/env python3
"""
人脸识别解锁系统 - 启动器
"""
import sys
import os

# 添加core目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x run.py

# 创建README
cat > README.md << 'EOF'
# 人脸识别解锁系统

## 文件结构
face_unlock_system/
├── run.py              # 主启动文件
├── config.json         # 配置文件
├── core/
│   ├── main.py        # 核心程序
│   ├── train_model.py # 训练程序
│   └── capture.py     # 拍照程序
├── utils/
│   ├── mac_trigger.py # Mac触发工具
│   └── trigger_handler.py
├── models/            # 模型文件
│   └── face_model.pkl
├── faces/             # 人脸数据
│   └── user1/
├── logs/              # 日志文件
└── backup_old/        # 旧文件备份
## 使用方法

### 运行系统
```bash
python3 run.py

### 训练模型
python3 core/train_model.py
### 拍照采集
python3 core/capture.py
### 测试Mac解锁
python3 utils/mac_trigger.py
### 配置说明
编辑 ⁠config.json 文件设置Mac连接信息和其他参数。
EOF
echo
echo "4. 创建快捷命令..."
创建便捷脚本
cat > face_unlock << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 run.py
EOF
chmod +x face_unlock
echo
echo "✓ 整理完成！"
echo
echo "新的文件结构："
tree -L 2 -I "pycache|*.pyc|backup_old"
echo
echo "使用方法："
echo "  ./face_unlock     # 运行系统"
echo "  python3 run.py    # 或使用Python运行"

### 执行整理：
```bash
cd ~/face_unlock_system

# 创建并运行整理脚本
chmod +x cleanup.sh
./cleanup.sh
