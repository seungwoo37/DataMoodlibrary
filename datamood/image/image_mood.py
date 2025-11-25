import cv2
from fer import FER

class EmotionAnalyzer:
    def __init__(self):
        self.detector = FER(mtcnn=True)
    
    def analyze(self, image_path):
        img=cv2.imread(image_path)

        if img is None:
            raise ValueError("이미지를 찾을 수 없습니다.")
        
        result = self.detector.detect_emotions(img)

        if len(result)==0:
            return {'message':'얼굴이 감지되지 않았습니다!'}
        
        emotions = result[0]['emotions']
        emotion = max(emotions, key=emotions.get)

        return{
            'emotion':emotion,
            'confidence':emotions[emotion],
            'detail': emotions
        }