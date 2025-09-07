#!/usr/bin/env python3
"""
Mac解锁模块 v2 - 支持多种解锁方式
"""
import subprocess
import json
import os

class MacUnlockerV2:
    def __init__(self):
        # 加载配置
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.mac_config = self.config.get('mac', {})
    
    def unlock_via_ssh(self, user):
        """通过SSH解锁Mac"""
        if not self.mac_config.get('enabled'):
            print("Mac解锁未启用")
            return False
        
        host = self.mac_config['host']
        username = self.mac_config['username']
        password = self.mac_config['password']
        
        print(f"🔓 正在为 {user} 解锁Mac...")
        
        # 方法1：使用osascript唤醒并输入密码
        unlock_script = f'''
        osascript -e 'tell application "System Events"
            key code 123
            delay 0.5
            keystroke "{password}"
            key code 36
        end tell'
        '''
        
        # SSH命令
        ssh_cmd = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{host} "{unlock_script}"'
        
        try:
            # 先安装sshpass
            subprocess.run(['which', 'sshpass'], check=True, capture_output=True)
        except:
            print("安装sshpass...")
            subprocess.run(['sudo', 'apt', 'install', '-y', 'sshpass'])
        
        # 执行解锁
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Mac解锁成功！")
            return True
        else:
            print(f"✗ 解锁失败: {result.stderr}")
            return False
    
    def wake_mac(self):
        """唤醒Mac（Wake-on-LAN）"""
        mac_address = self.mac_config.get('mac_address')
        if mac_address:
            subprocess.run(['wakeonlan', mac_address])
            print("📶 发送唤醒信号")

if __name__ == "__main__":
    unlocker = MacUnlockerV2()
    unlocker.unlock_via_ssh("test_user")
