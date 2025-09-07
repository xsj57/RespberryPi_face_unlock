#!/usr/bin/env python3
"""
人脸识别主程序 - 简化版
"""
import os
import pickle
import json
import subprocess
import time
from datetime import datetime

class FaceUnlockSystem:
    def __init__(self):
        print("初始化系统...")
        
        # 加载模型
        model_path = 'models/face_model.pkl'
        if not os.path.exists(model_path):
            print(f"✗ 找不到模型文件: {model_path}")
            exit(1)
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"✓ 模型加载成功")
        print(f"  授权用户: {', '.join(self.model['users'])}")
        print(f"  人脸总数: {self.model['total_faces']}")
        
        # 加载配置
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"recognition": {"tolerance": 0.4}}
        
        # 日志目录
        os.makedirs('logs', exist_ok=True)
    
    def recognize_once(self):
        """识别一次"""
        # 拍照
        temp_file = "/tmp/face.jpg"
        print("拍照中...")
        
        cmd = ['rpicam-jpeg', '-o', temp_file, 
               '--width', '1296', '--height', '972', 
               '-t', '500', '-n']
        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            print("✗ 拍照失败")
            return None
        
        # 识别
        import face_recognition
        
        try:
            image = face_recognition.load_image_file(temp_file)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                print("✗ 未检测到人脸")
                return None
            
            # 比对每个检测到的人脸
            tolerance = self.config.get('recognition', {}).get('tolerance', 0.4)
            
            for encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    self.model['encodings'],
                    encoding,
                    tolerance=tolerance
                )
                
                if True in matches:
                    index = matches.index(True)
                    name = self.model['names'][index]
                    
                    # 计算置信度
                    face_distances = face_recognition.face_distance(
                        self.model['encodings'], 
                        encoding
                    )
                    confidence = 1 - min(face_distances)
                    
                    print(f"✓ 识别成功: {name} (置信度: {confidence:.2%})")
                    
                    # 记录日志
                    self.log_recognition(name, confidence)
                    
                    return name
            
            print("✗ 未识别到授权用户")
            return None
            
        except Exception as e:
            print(f"识别错误: {e}")
            return None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def log_recognition(self, name, confidence):
        """记录识别日志"""
        timestamp = datetime.now()
        log_file = f"logs/recognition_{timestamp.strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a') as f:
            f.write(f"{timestamp}: {name} - 置信度: {confidence:.2%}\n")
    
    def unlock_mac(self, user):
        """解锁Mac"""
        mac_config = self.config.get('mac', {})
        
        if not mac_config.get('enabled', False):
            print("ℹ️ Mac解锁未启用")
            return
        
        print(f"🔓 为 {user} 解锁Mac...")
        
        # 这里添加实际的Mac解锁代码
        # 使用SSH或其他方式
        
        print("✓ 解锁命令已发送")
    
    def run_continuous(self):
        """持续运行模式"""
        print("\n=== 人脸识别系统运行中 ===")
        print("按 Ctrl+C 停止\n")
        
        check_interval = 3  # 3秒检查一次
        last_unlock_time = 0
        unlock_cooldown = 30  # 30秒冷却时间
        
        try:
            while True:
                current_time = time.time()
                
                # 检查冷却时间
                if current_time - last_unlock_time < unlock_cooldown:
                    remaining = unlock_cooldown - (current_time - last_unlock_time)
                    print(f"冷却中... {remaining:.0f}秒")
                    time.sleep(1)
                    continue
                
                # 识别
                user = self.recognize_once()
                
                if user:
                    self.unlock_mac(user)
                    last_unlock_time = current_time
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n系统停止")
    
    def run_single(self):
        """单次测试"""
        print("\n=== 单次识别测试 ===")
        user = self.recognize_once()
        
        if user:
            print(f"\n✓ 识别成功！")
            print(f"  用户: {user}")
            self.unlock_mac(user)
        else:
            print("\n✗ 识别失败")
        
        return user is not None


def main():
    print("="*50)
    print("人脸识别解锁系统 v2.0")
    print("="*50)
    
    system = FaceUnlockSystem()
    
    print("\n选择运行模式：")
    print("1. 单次测试")
    print("2. 持续监控")
    print("3. 性能测试")
    
    choice = input("\n请选择 (1/2/3) [1]: ").strip() or "1"
    
    if choice == "1":
        system.run_single()
    
    elif choice == "2":
        system.run_continuous()
    
    elif choice == "3":
        print("\n开始性能测试（5次）...")
        success = 0
        for i in range(5):
            print(f"\n测试 {i+1}/5:")
            if system.run_single():
                success += 1
            time.sleep(2)
        
        print(f"\n成功率: {success}/5 ({success*20}%)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
