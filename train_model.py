#!/usr/bin/env python3
"""
人脸识别模型训练脚本 - 独立版本
不依赖采集模块
"""
import os
import pickle
import json
from datetime import datetime

# 检查face_recognition库
try:
    import face_recognition
    import cv2
    import numpy as np
except ImportError as e:
    print(f"错误：缺少必要的库 - {e}")
    print("请安装：pip3 install face-recognition opencv-python numpy")
    exit(1)

class FaceModelTrainer:
    def __init__(self, faces_dir="faces", model_dir="models"):
        self.faces_dir = faces_dir
        self.model_dir = model_dir
        
        # 创建模型目录
        os.makedirs(model_dir, exist_ok=True)
        
        # 加载配置
        self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "authorized_users": [],
                "recognition_tolerance": 0.4
            }
    
    def scan_face_data(self):
        """扫描人脸数据目录"""
        if not os.path.exists(self.faces_dir):
            print(f"✗ 未找到人脸数据目录: {self.faces_dir}")
            return {}
        
        face_data = {}
        
        # 扫描每个用户目录
        for person_name in os.listdir(self.faces_dir):
            person_dir = os.path.join(self.faces_dir, person_name)
            
            if not os.path.isdir(person_dir):
                continue
            
            # 统计图片数量
            images = [f for f in os.listdir(person_dir) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if images:
                face_data[person_name] = {
                    'path': person_dir,
                    'count': len(images),
                    'images': images
                }
        
        return face_data
    
    def train_model(self):
        """训练人脸识别模型"""
        print("\n=== 开始训练人脸识别模型 ===\n")
        
        # 扫描数据
        face_data = self.scan_face_data()
        
        if not face_data:
            print("✗ 没有找到任何人脸数据")
            print("\n请先运行采集程序：")
            print("  python3 capture_final.py")
            return False
        
        # 显示找到的数据
        print("找到以下用户数据：")
        for name, info in face_data.items():
            print(f"  - {name}: {info['count']} 张照片")
        print()
        
        # 开始训练
        known_encodings = []
        known_names = []
        
        total_images = sum(info['count'] for info in face_data.values())
        processed = 0
        
        print(f"处理 {total_images} 张图片...")
        print("-" * 40)
        
        for person_name, info in face_data.items():
            print(f"\n处理 {person_name} 的照片...")
            person_encodings = []
            failed_count = 0
            
            for img_name in info['images']:
                img_path = os.path.join(info['path'], img_name)
                processed += 1
                
                # 显示进度
                progress = processed / total_images * 100
                print(f"\r[{progress:5.1f}%] 处理: {img_name[:30]}...", end="")
                
                try:
                    # 加载图片
                    image = face_recognition.load_image_file(img_path)
                    
                    # 查找人脸
                    face_locations = face_recognition.face_locations(image)
                    
                    if face_locations:
                        # 生成编码（只取第一张脸）
                        encoding = face_recognition.face_encodings(image, face_locations)[0]
                        person_encodings.append(encoding)
                        known_encodings.append(encoding)
                        known_names.append(person_name)
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    print(f"\n  ⚠ 处理失败: {img_name} - {e}")
                    failed_count += 1
            
            print(f"\n  ✓ {person_name}: 成功处理 {len(person_encodings)}/{info['count']} 张")
            if failed_count > 0:
                print(f"  ⚠ {failed_count} 张处理失败")
        
        # 保存模型
        if known_encodings:
            model_data = {
                'encodings': known_encodings,
                'names': known_names,
                'tolerance': self.config.get('recognition_tolerance', 0.4),
                'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_faces': len(known_encodings),
                'users': list(set(known_names))
            }
            
            model_path = os.path.join(self.model_dir, 'face_model.pkl')
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print("\n" + "="*50)
            print("✓ 模型训练完成！")
            print(f"  - 模型文件: {model_path}")
            print(f"  - 总人脸数: {len(known_encodings)}")
            print(f"  - 用户数: {len(set(known_names))}")
            print(f"  - 用户列表: {', '.join(set(known_names))}")
            
            # 更新配置文件中的用户列表
            self.config['authorized_users'] = list(set(known_names))
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"  - 配置文件已更新")
            
            return True
        else:
            print("\n✗ 没有成功处理任何人脸")
            return False
    
    def test_model(self):
        """测试模型"""
        model_path = os.path.join(self.model_dir, 'face_model.pkl')
        
        if not os.path.exists(model_path):
            print("✗ 模型文件不存在")
            return
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        print("\n=== 模型信息 ===")
        print(f"训练时间: {model_data.get('trained_at', '未知')}")
        print(f"人脸总数: {model_data.get('total_faces', 0)}")
        print(f"用户列表: {', '.join(model_data.get('users', []))}")
        print(f"识别阈值: {model_data.get('tolerance', 0.4)}")


def main():
    print("="*50)
    print("人脸识别模型训练系统")
    print("="*50)
    
    print("\n选择操作：")
    print("1. 训练新模型")
    print("2. 查看现有模型")
    print("3. 查看人脸数据")
    
    choice = input("\n请选择 (1/2/3) [1]: ").strip() or "1"
    
    trainer = FaceModelTrainer()
    
    if choice == "1":
        # 训练模型
        success = trainer.train_model()
        
        if success:
            print("\n下一步：")
            print("1. 测试识别: python3 test_recognition.py")
            print("2. 启动系统: python3 main.py")
            
    elif choice == "2":
        # 查看模型
        trainer.test_model()
        
    elif choice == "3":
        # 查看数据
        face_data = trainer.scan_face_data()
        
        if face_data:
            print("\n=== 人脸数据统计 ===")
            total = 0
            for name, info in face_data.items():
                print(f"{name:15} : {info['count']:3} 张照片")
                total += info['count']
            print("-" * 25)
            print(f"{'总计':15} : {total:3} 张照片")
        else:
            print("✗ 没有找到人脸数据")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被中断")
    except Exception as e:
        print(f"\n错误: {e}")
