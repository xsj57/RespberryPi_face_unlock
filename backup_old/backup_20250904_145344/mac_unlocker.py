import subprocess
import paramiko
import os

class MacUnlocker:
    def __init__(self, mac_ip, mac_username, mac_password):
        self.mac_ip = mac_ip
        self.mac_username = mac_username
        self.mac_password = mac_password
    
    def unlock_via_ssh(self):
        """通过SSH解锁Mac（需要Mac开启远程登录）"""
        try:
            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接到Mac
            ssh.connect(
                self.mac_ip, 
                username=self.mac_username, 
                password=self.mac_password
            )
            
            # 执行解锁命令（使用AppleScript）
            unlock_script = f'''
            osascript -e 'tell application "System Events" to keystroke "{self.mac_password}"'
            osascript -e 'tell application "System Events" to keystroke return'
            '''
            
            stdin, stdout, stderr = ssh.exec_command(unlock_script)
            
            ssh.close()
            return True
            
        except Exception as e:
            print(f"解锁失败: {e}")
            return False
    
    def unlock_via_vnc(self):
        """通过VNC解锁（备选方案）"""
        try:
            # 使用vncdotool或其他VNC工具
            cmd = f"vncdo -s {self.mac_ip}:5900 type {self.mac_password} key Return"
            subprocess.run(cmd, shell=True)
            return True
        except Exception as e:
            print(f"VNC解锁失败: {e}")
            return False
    
    def wake_on_lan(self, mac_address):
        """唤醒Mac（如果处于睡眠状态）"""
        try:
            # 安装wakeonlan: sudo apt-get install wakeonlan
            cmd = f"wakeonlan {mac_address}"
            subprocess.run(cmd, shell=True)
            return True
        except Exception as e:
            print(f"唤醒失败: {e}")
            return False
