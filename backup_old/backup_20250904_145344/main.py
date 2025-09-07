#!/usr/bin/env python3
import cv2
import time
import json
import os
from face_recognition_module import FaceRecognizer
from mac_unlocker import MacUnlocker
from trigger_handler import TriggerHandler

class FaceUnlockSystem:
    def __init__(self, config_file="config.json"):
        # 加载配置
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # 初始化各模块
        self.recognizer = FaceRecognizer()
        self.unlocker = MacUnlocker(
            self.config['mac_ip'],
            self.config['mac_username'],
            self.config['mac_password']
        )
        self.trigger = TriggerHandler(self.process_unlock)
        
        # OV5647摄像头初始化
        self.init_ov5647_camera()
        
        # 加载人脸模型
        if not self.recognizer.load_model():
            print("警告：未找到训练模型，请先运行训练程序")
    
    def init_ov5647_camera(self):
        """初始化OV5647摄像头"""
        # 尝试多种方式
        for i in range(4):
            try:
                self.camera = cv2.VideoCapture(i, cv2.CAP_V4L2)
                if self.camera.isOpened():
                    # OV5647设置
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1296)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 972)
                    self.camera.set(cv2.CAP_PROP_FPS, 30)
                    self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    ret, frame = self.camera.read()
                    if ret:
                        print(f"OV5647摄像头初始化成功 (/dev/video{i})")
                        return
                self.camera.release()
            except:
                pass
        
        # 使用默认方式
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("使用默认摄像头设置")
    
    def process_unlock(self):
        """处理解锁流程 - 针对OV5647优化"""
        print("开始人脸识别...")
        
        # 预热摄像头（OV5647需要）
        for _ in range(5):
            self.camera.read()
            time.sleep(0.1)
        
        # 进行多次识别以提高准确率
        recognition_results = []
        max_attempts = 5
        
        for i in range(max_attempts):
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # OV5647图像增强
            frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            
            names, locations = self.recognizer.recognize(frame)
            
            # 检查是否识别到授权用户
            for name in names:
                if name in self.config['authorized_users']:
                    recognition_results.append(name)
                    break
            
            time.sleep(0.2)

        
        # 判断识别结果
        if len(recognition_results) >= 3:  # 至少3次识别成功
            recognized_user = max(set(recognition_results), key=recognition_results.count)
            print(f"识别成功：{recognized_user}")
            
            # 执行解锁
            if self.unlocker.unlock_via_ssh():
                print("Mac解锁成功！")
                self.log_access(recognized_user, True)
                return True
            else:
                print("Mac解锁失败")
                self.log_access(recognized_user, False)
                return False
        else:
            print("人脸识别失败")
            self.log_access("Unknown", False)
            return False
    
    def log_access(self, user, success):
        """记录访问日志"""
        log_entry = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': user,
            'success': success
        }
        
        log_file = 'access_log.json'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        # 只保留最近100条记录
        if len(logs) > 100:
            logs = logs[-100:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def run(self):
        """运行主程序"""
        print("人脸解锁系统已启动")
        print(f"Web界面地址: http://{self.config['raspberry_pi_ip']}:5000")
        
        # 设置触发器
        if self.config['trigger_type'] == 'gpio':
            self.trigger.setup_gpio_button(self.config['gpio_pin'])
            print(f"GPIO按钮已设置在引脚 {self.config['gpio_pin']}")
        
        if self.config['trigger_type'] == 'web' or self.config['enable_web']:
            self.trigger.setup_web_trigger(5000)
            print("Web触发器已启动")
        
        try:
            # 保持程序运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n系统关闭")
            self.camera.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    system = FaceUnlockSystem()
    system.run()
