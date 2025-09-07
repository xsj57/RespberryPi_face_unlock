#!/usr/bin/env python3
from face_capture_optimized import OptimizedFaceCapture
from face_recognition_module import FaceRecognizer
import json
import os

def main():
    print("=== 人脸解锁系统初始设置 ===")
    
    # 检查配置文件
    if not os.path.exists('config.json'):
        print("错误：未找到config.json配置文件！")
        print("请先创建并配置config.json文件")
        return
    
    # 读取配置
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("\n当前配置的授权用户：")
    for user in config['authorized_users']:
        print(f"  - {user}")
    
    choice = input("\n选择操作：\n1. 采集人脸数据\n2. 训练模型\n3. 完整设置（采集+训练）\n请选择 (1/2/3): ")
    
    if choice in ['1', '3']:
        # 使用优化的采集模块
        capture = OptimizedFaceCapture(preview_fps=60)
        
        for user in config['authorized_users']:
            print(f"\n准备采集 {user} 的人脸数据")
            print("提示：请确保光线充足，正对摄像头")
            input("按Enter开始采集...")
            
            # 使用交互式采集
            success = capture.capture_faces_interactive(user, target_count=20)
            
            if not success:
                print(f"跳过 {user}")
                continue
    
    if choice in ['2', '3']:
        # 训练模型
        print("\n开始训练人脸识别模型...")
        recognizer = FaceRecognizer()
        
        # 创建模型目录
        os.makedirs('models', exist_ok=True)
        recognizer.model_path = 'models/face_model.pkl'
        
        recognizer.train_model()
        print("\n训练完成！")
    
    print("\n设置完成！你可以运行 python3 main.py 启动系统")

if __name__ == "__main__":
    main()
