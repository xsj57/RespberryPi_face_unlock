#!/usr/bin/env python3
"""
最终版人脸采集工具 - 使用rpicam命令行
简单、可靠、无复杂依赖
"""
import subprocess
import os
import time
from datetime import datetime

# 可选的人脸检测
HAS_CV2 = False
try:
    import cv2
    # 使用本地下载的cascade文件
    if os.path.exists('haarcascade_frontalface_default.xml'):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        HAS_CV2 = True
        print("✓ 人脸检测已启用")
except ImportError:
    print("⚠ OpenCV未安装，人脸检测已禁用")

class FinalCapture:
    def __init__(self, save_dir="faces"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def take_photo_rpicam(self, output_path):
        """使用rpicam-jpeg拍照 - 核心功能"""
        cmd = [
            'rpicam-jpeg',
            '-o', output_path,
            '--width', '1296',
            '--height', '972',
            '-t', '100',  # 100ms延迟
            '-n'  # 无预览
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def preview_camera(self):
        """打开摄像头预览（可选）"""
        print("\n正在打开摄像头预览...")
        print("调整好位置后关闭预览窗口")
        subprocess.run(['rpicam-hello', '-t', '5000'])
    
    def check_face(self, image_path):
        """检查是否有人脸（可选功能）"""
        if not HAS_CV2:
            return True  # 没有OpenCV时总是返回True
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return True
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces) > 0
        except:
            return True
    
    def capture_photos(self, person_name, target_count=20):
        """主采集函数"""
        person_dir = os.path.join(self.save_dir, person_name)
        os.makedirs(person_dir, exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"采集 {person_name} 的照片")
        print(f"目标数量: {target_count}")
        print(f"{'='*50}")
        
        print("\n控制说明:")
        print("  Enter  - 拍照")
        print("  p      - 预览摄像头")
        print("  a      - 自动模式")
        print("  q      - 退出")
        print("")
        
        count = 0
        failed_count = 0
        
        while count < target_count:
            # 显示进度
            progress = "█" * count + "░" * (target_count - count)
            print(f"\r进度: [{progress}] {count}/{target_count}", end="")
            
            # 获取输入
            cmd = input(f"\n[{count}/{target_count}] > ").strip().lower()
            
            if cmd == 'q':
                print("\n用户退出")
                break
            
            elif cmd == 'p':
                # 预览
                self.preview_camera()
            
            elif cmd == 'a':
                # 自动模式
                print("\n自动模式开始（2秒间隔）")
                print("按 Ctrl+C 停止\n")
                
                try:
                    while count < target_count:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = f"{person_name}_{timestamp}.jpg"
                        filepath = os.path.join(person_dir, filename)
                        
                        print(f"拍摄 {count+1}/{target_count}...", end="")
                        
                        if self.take_photo_rpicam(filepath):
                            if HAS_CV2 and not self.check_face(filepath):
                                os.remove(filepath)
                                print(" ✗ (无人脸)")
                            else:
                                count += 1
                                print(" ✓")
                        else:
                            print(" ✗ (失败)")
                            failed_count += 1
                            if failed_count > 3:
                                print("\n错误：连续失败，请检查摄像头")
                                return False
                        
                        if count < target_count:
                            time.sleep(2)
                            
                except KeyboardInterrupt:
                    print("\n\n自动模式停止")
            
            else:  # Enter或其他 - 拍照
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"{person_name}_{timestamp}.jpg"
                filepath = os.path.join(person_dir, filename)
                
                print("拍照中...", end="")
                
                if self.take_photo_rpicam(filepath):
                    if HAS_CV2 and not self.check_face(filepath):
                        os.remove(filepath)
                        print(" ✗ (未检测到人脸，请调整位置)")
                    else:
                        count += 1
                        print(f" ✓ 已保存")
                        failed_count = 0
                else:
                    print(" ✗ (拍照失败)")
                    failed_count += 1
                    if failed_count > 3:
                        print("\n错误：连续失败，请检查摄像头")
                        return False
        
        # 完成统计
        print(f"\n{'='*50}")
        print(f"✓ 完成！共采集 {count} 张照片")
        if count > 0:
            print(f"保存位置: {person_dir}/")
            
            # 列出文件
            files = sorted(os.listdir(person_dir))
            print(f"\n最新的5张照片:")
            for f in files[-5:]:
                size = os.path.getsize(os.path.join(person_dir, f)) // 1024
                print(f"  - {f} ({size}KB)")
        
        return count > 0


def main():
    print("="*50)
    print("树莓派5 人脸采集系统")
    print("="*50)
    
    # 测试rpicam
    print("\n正在测试摄像头...")
    test_result = subprocess.run(['rpicam-hello', '-t', '1'], capture_output=True)
    if test_result.returncode != 0:
        print("✗ 摄像头测试失败！")
        print("请检查：")
        print("1. 摄像头是否正确连接")
        print("2. 运行: rpicam-hello -t 2000")
        return
    
    print("✓ 摄像头正常\n")
    
    # 获取用户输入
    name = input("输入用户名: ").strip()
    if not name:
        print("用户名不能为空")
        return
    
    count = input("拍摄数量 [20]: ").strip()
    count = int(count) if count else 20
    
    # 开始采集
    capture = FinalCapture()
    success = capture.capture_photos(name, count)
    
    if success:
        print("\n下一步：")
        print("1. 检查照片: ls -la faces/" + name)
        print("2. 训练模型: python3 setup_training.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被中断")
    except Exception as e:
        print(f"\n错误: {e}")
