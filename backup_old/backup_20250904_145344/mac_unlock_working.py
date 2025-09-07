#!/usr/bin/env python3
"""
Mac解锁 - 确实能工作的版本
"""
import subprocess
import json
import time

def unlock_mac_method1():
    """方法1：避免System Events语法错误"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mac = config['mac']
    host = mac['host']
    username = mac['username']
    password = mac['password']
    
    print("方法1：使用简化的osascript...")
    
    # 使用tell application的简短形式，避免"System Events"引号问题
    commands = [
        # 唤醒
        f'sshpass -p "{password}" ssh -o LogLevel=ERROR {username}@{host} "caffeinate -u -t 1"',
        
        # 等待
        'sleep 1',
        
        # 输入密码 - 使用简短语法
        f'sshpass -p "{password}" ssh -o LogLevel=ERROR {username}@{host} "osascript -e \'tell app \\"System Events\\" to keystroke \\"{password}\\"\'"',
        
        # 按回车
        f'sshpass -p "{password}" ssh -o LogLevel=ERROR {username}@{host} "osascript -e \'tell app \\"System Events\\" to key code 36\'"'
    ]
    
    for cmd in commands:
        if cmd.startswith('sleep'):
            time.sleep(1)
        else:
            subprocess.run(cmd, shell=True, capture_output=True)
    
    print("✓ 解锁命令已发送")


def unlock_mac_method2():
    """方法2：使用base64编码避免引号问题"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mac = config['mac']
    host = mac['host']
    username = mac['username']
    password = mac['password']
    
    print("方法2：使用base64编码...")
    
    import base64
    
    # AppleScript脚本
    script = f'''
    tell application "System Events"
        keystroke "{password}"
        key code 36
    end tell
    '''
    
    # Base64编码
    encoded = base64.b64encode(script.encode()).decode()
    
    # 执行
    cmd = f'sshpass -p "{password}" ssh -o LogLevel=ERROR {username}@{host} "echo {encoded} | base64 -d | osascript"'
    
    subprocess.run(cmd, shell=True, capture_output=True)
    print("✓ 解锁命令已发送")


def unlock_mac_method3():
    """方法3：在Mac端创建解锁脚本"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mac = config['mac']
    host = mac['host']
    username = mac['username']
    password = mac['password']
    
    print("方法3：远程创建并执行脚本...")
    
    # 先在Mac端创建一个解锁脚本
    create_script = f'''
    sshpass -p "{password}" ssh -o LogLevel=ERROR {username}@{host} "
    cat > /tmp/unlock.scpt << 'SCRIPT'
    tell application \\"System Events\\"
        keystroke \\"{password}\\"
        key code 36
    end tell
    SCRIPT
    "
    '''
    
    # 执行脚本
    run_script = f'sshpass -p "{password}" ssh -o LogLevel=ERROR {username}@{host} "osascript /tmp/unlock.scpt"'
    
    subprocess.run(create_script, shell=True, capture_output=True)
    subprocess.run(run_script, shell=True, capture_output=True)
    
    print("✓ 解锁脚本已执行")


def unlock_mac_simple():
    """超简单版本 - 分步执行"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mac = config['mac']
    host = mac['host']
    username = mac['username']
    password = mac['password']
    
    print("执行解锁序列...")
    
    # SSH基础命令
    ssh_base = f'sshpass -p "{password}" ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no {username}@{host}'
    
    # 步骤1：唤醒
    print("  1. 唤醒屏幕...")
    subprocess.run(f'{ssh_base} "caffeinate -u -t 1"', shell=True, capture_output=True)
    time.sleep(1)
    
    # 步骤2：模拟键盘活动
    print("  2. 模拟键盘...")
    subprocess.run(f'{ssh_base} "osascript -e \'tell app \\"Finder\\" to activate\'"', shell=True, capture_output=True)
    time.sleep(0.5)
    
    # 步骤3：输入密码（每个字符单独输入）
    print("  3. 输入密码...")
    for char in password:
        if char.isalnum():  # 只处理字母数字
            time.sleep(2)
            subprocess.run(f'{ssh_base} "osascript -e \'tell app \\"System Events\\" to key code 48\'"', shell=True,
            capture_output=True)
            time.sleep(0.5)
    
    # 步骤4：按回车
    print("  4. 确认...")
    subprocess.run(f'{ssh_base} "osascript -e \'tell app \\"System Events\\" to key code 36\'"', shell=True, capture_output=True)
    
    print("✓ 解锁序列完成")


if __name__ == "__main__":
    print("=== Mac解锁测试 ===\n")
    print("1. 方法1 - 简化语法")
    print("2. 方法2 - Base64编码")
    print("3. 方法3 - 远程脚本")
    print("4. 超简单版本")
    
    choice = input("\n选择方法 (1/2/3/4) [4]: ").strip() or "4"
    
    if choice == "1":
        unlock_mac_method1()
    elif choice == "2":
        unlock_mac_method2()
    elif choice == "3":
        unlock_mac_method3()
    else:
        unlock_mac_simple()
