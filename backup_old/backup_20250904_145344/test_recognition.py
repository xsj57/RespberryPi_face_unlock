#!/usr/bin/env python3
"""测试人脸识别"""
import os
import pickle
import subprocess
import time

def test_with_photo():
    """拍照并测试识别"""
    if not os.path.exists('models/face_model.pkl'):
        print("✗ 请先训练模型: python3 train_model.py")
        return
    
    # 拍照
    test_file = "/tmp/test_face.jpg"
    print("拍照测试中...")
    
    cmd = ['rpicam-jpeg', '-o', test_file, '--width', '1296', '--height', '972', '-t', '1000']
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0:
        print("✗ 拍照失败")
        return
    
    # 加载模型
    import face_recognition
    
    with open('models/face_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    # 识别
    unknown_image = face_recognition.load_image_file(test_file)
    unknown_encodings = face_recognition.face_encodings(unknown_image)
    
    if not unknown_encodings:
        print("✗ 未检测到人脸")
        return
    
    # 比对
    for unknown_encoding in unknown_encodings:
        matches = face_recognition.compare_faces(
            model['encodings'], 
            unknown_encoding,
            tolerance=model.get('tolerance', 0.4)
        )
        
        if True in matches:
            match_index = matches.index(True)
            name = model['names'][match_index]
            print(f"✓ 识别成功: {name}")
        else:
            print("✗ 未识别出已知用户")
    
    # 清理
    os.remove(test_file)

if __name__ == "__main__":
    print("=== 人脸识别测试 ===")
    print("请面向摄像头...")
    time.sleep(2)
    test_with_photo()
