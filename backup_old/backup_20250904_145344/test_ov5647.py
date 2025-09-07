#!/usr/bin/env python3
import cv2
import subprocess
import sys

def test_ov5647():
    """测试OV5647摄像头"""
    print("=== OV5647摄像头测试 ===\n")
    
    # 1. 检查系统识别
    print("1. 检查摄像头识别...")
    try:
        result = subprocess.run(['vcgencmd', 'get_camera'], 
                              capture_output=True, text=True)
        print(f"   {result.stdout.strip()}")
    except:
        print("   vcgencmd不可用（树莓派5正常）")
    
    # 2. 检查v4l2设备
    print("\n2. 检查V4L2设备...")
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except:
        print("   请安装v4l-utils: sudo apt-get install v4l-utils")
    
    # 3. 测试libcamera
    print("\n3. 测试libcamera...")
    try:
        result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                              capture_output=True, text=True)
        if 'ov5647' in result.stdout.lower():
            print("   ✓ 检测到OV5647摄像头")
        print(result.stdout)
    except Exception as e:
        print(f"   libcamera测试失败: {e}")
    
    # 4. 测试OpenCV访问
    print("\n4. 测试OpenCV访问...")
    test_resolutions = [
        (2592, 1944, 15, "5MP"),
        (1920, 1080, 30, "1080p"),
        (1296, 972, 42, "720p+"),
        (640, 480, 90, "VGA")
    ]
    
    for width, height, fps, name in test_resolutions:
        print(f"\n   测试 {name} ({width}x{height} @ {fps}fps)...")
        
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        ret, frame = cap.read()
        if ret:
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"   ✓ 成功: 实际 {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # 保存测试图像
            filename = f"test_ov5647_{name}.jpg"
            cv2.imwrite(filename, frame)
            print(f"   保存测试图像: {filename}")
        else:
            print(f"   ✗ 失败")
        
        cap.release()
    
    print("\n测试完成！")
    print("\n建议使用的分辨率：")
    print("  - 人脸识别: 1296x972 (平衡速度和质量)")
    print("  - 高质量采集: 1920x1080")
    print("  - 快速预览: 640x480")

if __name__ == "__main__":
    test_ov5647()
