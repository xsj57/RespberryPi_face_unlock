#!/usr/bin/env python3
"""
测试新的解锁方法
"""
import requests
import json

with open('config.json', 'r') as f:
    config = json.load(f)

mac_host = config['mac']['host']

# 测试v2接口（更可靠的输入方法）
url = f"http://{mac_host}:5001/unlock_v2"
data = {
    'user': 'test',
    'key': 'face_unlock_2024'
}

print("测试新的解锁方法...")
response = requests.post(url, json=data, timeout=10)

if response.status_code == 200:
    print("✓ 解锁成功!")
    print(response.json())
else:
    print("✗ 解锁失败")
    print(response.text)
