#!/usr/bin/env python3
"""
人脸识别解锁系统 - 最终完整版
Face Recognition Unlock System - Final Version
"""
import os
import sys
import pickle
import json
import subprocess
import time
import requests
from datetime import datetime
import signal
import threading

# 尝试导入face_recognition
try:
    import face_recognition
    import numpy as np
    HAS_FACE_RECOGNITION = True
except ImportError:
    print("⚠ face_recognition未安装")
    print("安装命令: pip3 install --user face-recognition")
    HAS_FACE_RECOGNITION = False

class FaceUnlockSystem:
    def __init__(self):
        """初始化系统"""
        print("="*50)
        print("人脸识别解锁系统 v3.0")
        print("="*50)
        print("\n初始化中...")
        
        # 加载配置
        self.load_config()
        
        # 加载模型
        if not self.load_model():
            print("\n⚠ 模型加载失败")
            print("请运行: python3 train_model.py")
            sys.exit(1)
        
        # 初始化统计
        self.stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now()
        }
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("\n✓ 系统初始化完成")
        print("-"*50)
    
    def load_config(self):
        """加载配置文件"""
        config_file = 'config.json'
        
        if not os.path.exists(config_file):
            print(f"✗ 配置文件不存在: {config_file}")
            self.create_default_config()
        
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            
            # 验证必要配置
            if 'mac' not in self.config:
                self.config['mac'] = {
                    'enabled': False,
                    'host': 'localhost',
                    'port': 5001
                }
            
            if 'recognition' not in self.config:
                self.config['recognition'] = {
                    'tolerance': 0.4,
                    'check_interval': 3.0
                }
            
            print("✓ 配置加载成功")
            
            # 显示Mac配置状态
            mac_config = self.config.get('mac', {})
            if mac_config.get('enabled', False):
                print(f"  Mac解锁: 已启用 ({mac_config.get('host')})")
            else:
                print("  Mac解锁: 未启用")
                
        except json.JSONDecodeError as e:
            print(f"✗ 配置文件格式错误: {e}")
            self.create_default_config()
        except Exception as e:
            print(f"✗ 配置加载失败: {e}")
            sys.exit(1)
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
            "camera": {
                "type": "ov5647",
                "backend": "rpicam",
                "width": 1296,
                "height": 972
            },
            "mac": {
                "enabled": False,
                "host": "192.168.1.100",
                "port": 5001,
                "username": "your_username",
                "password": "your_password"
            },
            "recognition": {
                "tolerance": 0.4,
                "check_interval": 3.0,
                "confidence_threshold": 0.6
            },
            "authorized_users": ["user1"],
            "system": {
                "log_level": "INFO",
                "log_dir": "logs"
            }
        }
        
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print("✓ 已创建默认配置文件")
        self.config = default_config
    
    def load_model(self):
        """加载人脸识别模型"""
        model_path = 'models/face_model.pkl'
        
        if not os.path.exists(model_path):
            print(f"✗ 模型文件不存在: {model_path}")
            return False
        
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # 验证模型内容
            required_keys = ['encodings', 'names', 'users']
            for key in required_keys:
                if key not in self.model:
                    print(f"✗ 模型缺少必要数据: {key}")
                    return False
            
            print(f"✓ 模型加载成功")
            print(f"  授权用户: {', '.join(self.model.get('users', []))}")
            print(f"  人脸数据: {len(self.model.get('encodings', []))} 个")
            
            return True
            
        except Exception as e:
            print(f"✗ 模型加载错误: {e}")
            return False
    
    def capture_photo(self):
        """拍照"""
        temp_file = "/tmp/face_capture.jpg"
        
        # 使用rpicam-jpeg拍照
        cmd = [
            'rpicam-jpeg',
            '-o', temp_file,
            '--width', str(self.config.get('camera', {}).get('width', 1296)),
            '--height', str(self.config.get('camera', {}).get('height', 972)),
            '-t', '500',  # 0.5秒延迟
            '-n'  # 不显示预览
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                return temp_file
            else:
                print("✗ 拍照失败")
                if result.stderr:
                    print(f"  错误: {result.stderr.decode()}")
                return None
                
        except subprocess.TimeoutExpired:
            print("✗ 拍照超时")
            return None
        except Exception as e:
            print(f"✗ 拍照错误: {e}")
            return None
    
    def recognize_face(self, image_path):
        """识别人脸"""
        if not HAS_FACE_RECOGNITION:
            print("⚠ face_recognition库未安装")
            return None
        
        try:
            # 加载图片
            image = face_recognition.load_image_file(image_path)
            
            # 检测人脸并编码
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                print("✗ 未检测到人脸")
                return None
            
            print(f"  检测到 {len(face_locations)} 个人脸")
            
            # 获取人脸编码
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            # 识别每个人脸
            tolerance = self.config.get('recognition', {}).get('tolerance', 0.4)
            
            for face_encoding in face_encodings:
                # 比对已知人脸
                matches = face_recognition.compare_faces(
                    self.model['encodings'],
                    face_encoding,
                    tolerance=tolerance
                )
                
                if True in matches:
                    # 找到匹配的人脸
                    match_index = matches.index(True)
                    name = self.model['names'][match_index]
                    
                    # 计算置信度
                    face_distances = face_recognition.face_distance(
                        self.model['encodings'],
                        face_encoding
                    )
                    confidence = 1 - min(face_distances)
                    
                    # 检查置信度阈值
                    min_confidence = self.config.get('recognition', {}).get('confidence_threshold', 0.6)
                    if confidence >= min_confidence:
                        return {
                            'name': name,
                            'confidence': confidence,
                            'distance': min(face_distances)
                        }
                    else:
                        print(f"  置信度太低: {confidence:.1%} < {min_confidence:.1%}")
            
            print("✗ 未识别到授权用户")
            return None
            
        except Exception as e:
            print(f"✗ 识别错误: {e}")
            return None
    
    def unlock_mac(self, user):
        """解锁Mac电脑"""
        mac_config = self.config.get('mac', {})
        
        if not mac_config.get('enabled', False):
            print("ℹ Mac解锁未启用")
            return False
        
        print(f"🔓 触发Mac解锁...")
        
        try:
            # 构建请求URL
            host = mac_config.get('host', 'localhost')
            port = mac_config.get('port', 5001)
            url = f"http://{host}:{port}/unlock"
            
            # 发送解锁请求
            data = {
                'user': user,
                'key': 'face_unlock_2024'
            }
            
            # 增加超时时间和重试机制
            response = requests.post(url, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Mac解锁成功")
                print(f"  状态: {result.get('status')}")
                return True
            elif response.status_code == 401:
                print("✗ Mac解锁失败: 未授权")
                return False
            else:
                print(f"✗ Mac解锁失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("✗ Mac解锁超时 - 但解锁可能仍在进行中")
            # 超时不一定意味着失败，Mac端可能仍在处理
            return True
        except requests.exceptions.ConnectionError:
            print("✗ 无法连接到Mac解锁服务")
            print(f"  请确保Mac上的服务运行在 {host}:{port}")
            return False
        except Exception as e:
            print(f"✗ Mac解锁错误: {e}")
            return False
    
    def check_mac_service(self):
        """检查Mac服务状态"""
        mac_config = self.config.get('mac', {})
        
        if not mac_config.get('enabled', False):
            return False
        
        try:
            host = mac_config.get('host', 'localhost')
            port = mac_config.get('port', 5001)
            url = f"http://{host}:{port}/status"
            
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Mac服务正常: {result.get('status')}")
                return True
            else:
                print(f"⚠ Mac服务异常: HTTP {response.status_code}")
                return False
                
        except:
            print("⚠ Mac服务未响应")
            return False
    
    def run_once(self):
        """运行一次识别"""
        print("\n" + "="*40)
        print(f"识别开始 - {datetime.now().strftime('%H:%M:%S')}")
        print("-"*40)
        
        self.stats['total_attempts'] += 1
        
        # 拍照
        print("📷 拍照中...")
        photo_path = self.capture_photo()
        
        if not photo_path:
            self.stats['failed'] += 1
            return False
        
        # 识别
        print("🔍 识别中...")
        result = self.recognize_face(photo_path)
        
        # 清理临时文件
        try:
            os.remove(photo_path)
        except:
            pass
        
        if result:
            name = result['name']
            confidence = result['confidence']
            
            print(f"\n✓ 识别成功!")
            print(f"  用户: {name}")
            print(f"  置信度: {confidence:.1%}")
            
            self.stats['successful'] += 1
            
            # 解锁Mac
            if self.config.get('mac', {}).get('enabled', False):
                self.unlock_mac(name)
            
            # 记录日志
            self.log_event(f"识别成功: {name} ({confidence:.1%})")
            
            return True
        else:
            print("\n✗ 识别失败")
            self.stats['failed'] += 1
            self.log_event("识别失败: 未识别到授权用户")
            return False
    
    def run_continuous(self):
        """持续监控模式"""
        print("\n=== 持续监控模式 ===")
        print("按 Ctrl+C 停止\n")
        
        # 检查Mac服务
        if self.config.get('mac', {}).get('enabled', False):
            self.check_mac_service()
        
        interval = self.config.get('recognition', {}).get('check_interval', 3.0)
        last_success_time = 0
        cooldown = 30  # 成功后的冷却时间（秒）
        
        try:
            while True:
                current_time = time.time()
                
                # 检查冷却时间
                if last_success_time > 0 and current_time - last_success_time < cooldown:
                    remaining = cooldown - (current_time - last_success_time)
                    print(f"⏳ 冷却中... {remaining:.0f}秒", end='\r')
                    time.sleep(1)
                    continue
                
                # 执行识别
                success = self.run_once()
                
                if success:
                    last_success_time = current_time
                    print(f"\n⏸ 进入冷却期 {cooldown}秒\n")
                
                # 显示统计
                self.show_stats()
                
                # 等待下次检测
                print(f"\n💤 等待 {interval}秒...\n")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.shutdown()
    
    def run_manual(self):
        """手动触发模式"""
        print("\n=== 手动触发模式 ===")
        print("命令:")
        print("  Enter - 进行识别")
        print("  s     - 显示统计")
        print("  c     - 检查Mac服务")
        print("  q     - 退出")
        print("-"*40 + "\n")
        
        while True:
            try:
                cmd = input("\n按Enter识别 (s/c/q): ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 's':
                    self.show_stats()
                elif cmd == 'c':
                    self.check_mac_service()
                else:
                    self.run_once()
                    
            except KeyboardInterrupt:
                break
        
        self.shutdown()
    
    def run_test(self):
        """测试模式"""
        print("\n=== 测试模式 ===")
        
        tests = [
            ("相机测试", self.test_camera),
            ("模型测试", self.test_model),
            ("Mac服务测试", self.test_mac_service),
            ("完整流程测试", self.test_full_process)
        ]
        
        for name, test_func in tests:
            print(f"\n{name}...")
            print("-"*30)
            test_func()
            time.sleep(1)
        
        print("\n测试完成！")
    
    def test_camera(self):
        """测试相机"""
        photo = self.capture_photo()
        if photo:
            size = os.path.getsize(photo)
            print(f"✓ 相机正常 (照片大小: {size/1024:.1f}KB)")
            os.remove(photo)
        else:
            print("✗ 相机测试失败")
    
    def test_model(self):
        """测试模型"""
        if self.model:
            print(f"✓ 模型正常")
            print(f"  用户: {', '.join(self.model.get('users', []))}")
            print(f"  编码数: {len(self.model.get('encodings', []))}")
        else:
            print("✗ 模型未加载")
    
    def test_mac_service(self):
        """测试Mac服务"""
        if self.config.get('mac', {}).get('enabled', False):
            self.check_mac_service()
        else:
            print("ℹ Mac服务未启用")
    
    def test_full_process(self):
        """测试完整流程"""
        print("执行完整识别流程...")
        self.run_once()
    
    def show_stats(self):
        """显示统计信息"""
        runtime = datetime.now() - self.stats['start_time']
        total = self.stats['total_attempts']
        
        if total > 0:
            success_rate = (self.stats['successful'] / total) * 100
        else:
            success_rate = 0
        
        print("\n" + "="*40)
        print("📊 统计信息")
        print("-"*40)
        print(f"运行时间: {runtime}")
        print(f"总尝试: {total}")
        print(f"成功: {self.stats['successful']}")
        print(f"失败: {self.stats['failed']}")
        print(f"成功率: {success_rate:.1f}%")
        print("="*40)
    
    def log_event(self, message):
        """记录事件日志"""
        log_dir = self.config.get('system', {}).get('log_dir', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now()
        log_file = os.path.join(log_dir, f"face_unlock_{timestamp.strftime('%Y%m%d')}.log")
        
        try:
            with open(log_file, 'a') as f:
                f.write(f"{timestamp}: {message}\n")
        except Exception as e:
            print(f"⚠ 日志记录失败: {e}")
    
    def signal_handler(self, signum, frame):
        """信号处理"""
        print("\n\n⚠ 收到中断信号")
        self.shutdown()
    
    def shutdown(self):
        """关闭系统"""
        print("\n正在关闭系统...")
        self.show_stats()
        print("\n👋 再见！")
        sys.exit(0)


def main():
    """主函数"""
    # 检查是否在树莓派上运行
    if not os.path.exists('/usr/bin/rpicam-jpeg'):
        print("⚠ 警告: 未检测到rpicam-jpeg")
        print("  请确保在树莓派上运行")
        print("  或安装: sudo apt install -y rpicam-apps")
        print()
    
    # 初始化系统
    try:
        system = FaceUnlockSystem()
    except Exception as e:
        print(f"\n✗ 系统初始化失败: {e}")
        return 1
    
    # 显示菜单
    print("\n选择运行模式：")
    print("1. 单次识别")
    print("2. 手动触发")
    print("3. 持续监控")
    print("4. 测试模式")
    print("5. 查看配置")
    print("6. 退出")
    
    try:
        choice = input("\n选择 (1-6) [1]: ").strip() or "1"
        
        if choice == "1":
            # 单次识别
            system.run_once()
            
        elif choice == "2":
            # 手动触发
            system.run_manual()
            
        elif choice == "3":
            # 持续监控
            system.run_continuous()
            
        elif choice == "4":
            # 测试模式
            system.run_test()
            
        elif choice == "5":
            # 查看配置
            print("\n当前配置：")
            print("-"*40)
            print(json.dumps(system.config, indent=2, ensure_ascii=False))
            
        elif choice == "6":
            # 退出
            print("\n👋 再见！")
            return 0
            
        else:
            print("\n⚠ 无效选择")
            return 1
            
    except KeyboardInterrupt:
        system.shutdown()
    except Exception as e:
        print(f"\n✗ 运行错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
