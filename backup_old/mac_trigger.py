#!/usr/bin/env python3
"""
触发Mac解锁 - 通过HTTP请求
"""
import requests
import json

def trigger_mac_unlock(user="raspberry"):
    """发送解锁请求到Mac"""
    # 从config.json读取Mac地址
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mac_host = config['mac']['host']
    
    # 发送解锁请求
    url = f"http://{mac_host}:5001/unlock"
    data = {
        'user': user,
        'key': 'face_unlock_2024'
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print("✓ Mac解锁成功")
            return True
        else:
            print(f"✗ 解锁失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

def test_connection():
    """测试连接"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mac_host = config['mac']['host']
    url = f"http://{mac_host}:5001/test"
    
    try:
        response = requests.get(url, timeout=3)
        print(f"✓ 连接成功: {response.json()}")
        return True
    except:
        print("✗ 无法连接到Mac服务")
        return False

if __name__ == "__main__":
    print("测试Mac解锁服务...")
    
    if test_connection():
        print("\n触发解锁...")
        trigger_mac_unlock("test_user")
    else:
        print("\n请确保Mac上的服务正在运行：")
        print("python3 ~/face_unlock_server.py")
