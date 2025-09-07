#!/usr/bin/env python3
"""
触发Mac解锁 - 最终版
"""
import requests
import json
import time

class MacUnlocker:
    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.mac_host = self.config['mac']['host']
        self.base_url = f"http://{self.mac_host}:5001"
    
    def check_service(self):
        """检查Mac服务是否运行"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=2)
            if response.status_code == 200:
                print(f"✓ Mac服务正常: {response.json()}")
                return True
        except:
            pass
        print("✗ Mac服务未响应")
        return False
    
    def unlock(self, user="raspberry"):
        """发送解锁请求"""
        try:
            data = {
                'user': user,
                'key': 'face_unlock_2024'
            }
            
            response = requests.post(
                f"{self.base_url}/unlock",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✓ Mac解锁成功: {response.json()}")
                return True
            else:
                print(f"✗ 解锁失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ 请求失败: {e}")
            return False
    
    def wake_only(self):
        """仅唤醒屏幕"""
        try:
            response = requests.post(f"{self.base_url}/wake", timeout=3)
            print("✓ 屏幕已唤醒")
            return True
        except:
            return False

if __name__ == "__main__":
    unlocker = MacUnlocker()
    
    print("=== Mac解锁测试 ===\n")
    
    if unlocker.check_service():
        print("\n1. 解锁Mac")
        print("2. 仅唤醒屏幕")
        print("3. 连续测试")
        
        choice = input("\n选择 (1/2/3): ").strip()
        
        if choice == "1":
            unlocker.unlock("test_user")
        elif choice == "2":
            unlocker.wake_only()
        else:
            for i in range(3):
                print(f"\n测试 {i+1}/3")
                unlocker.unlock(f"test_{i+1}")
                time.sleep(5)
