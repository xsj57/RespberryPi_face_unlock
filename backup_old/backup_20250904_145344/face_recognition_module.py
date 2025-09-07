import face_recognition
import cv2
import numpy as np
import os
import pickle

class FaceRecognizer:
    def __init__(self, faces_dir="faces", model_path="face_model.pkl"):
        self.faces_dir = faces_dir
        self.model_path = model_path
        self.known_face_encodings = []
        self.known_face_names = []
        
    def train_model(self):
        """训练人脸识别模型"""
        print("开始训练人脸识别模型...")
        
        for person_name in os.listdir(self.faces_dir):
            person_dir = os.path.join(self.faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue
            
            person_encodings = []
            
            for image_file in os.listdir(person_dir):
                if not image_file.endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(person_dir, image_file)
                image = face_recognition.load_image_file(image_path)
                
                # 获取人脸编码
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    person_encodings.append(encodings[0])
            
            if person_encodings:
                # 计算平均编码
                avg_encoding = np.mean(person_encodings, axis=0)
                self.known_face_encodings.append(avg_encoding)
                self.known_face_names.append(person_name)
                print(f"已添加 {person_name} 的人脸数据")
        
        # 保存模型
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }, f)
        
        print("模型训练完成！")
    
    def load_model(self):
        """加载已训练的模型"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                return True
        return False
    
    def recognize(self, frame, tolerance=0.4):
        """识别单帧图像中的人脸"""
        # 缩小图像以加快处理速度
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # 检测人脸位置和编码
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            # 与已知人脸进行比较
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding, 
                tolerance=tolerance
            )
            name = "Unknown"
            
            # 计算距离找出最佳匹配
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encoding
            )
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index] and face_distances[best_match_index] < tolerance:
                    name = self.known_face_names[best_match_index]
            
            face_names.append(name)
        
        return face_names, face_locations
