import cv2
import numpy as np
from fer import FER
import os

class EmotionAnalyzer:
    def __init__(self, use_mtcnn=True):
        """
        초기화 메서드
        :param use_mtcnn: True일 경우 MTCNN을 사용하여 정확도를 높임 (속도는 느려짐)
        """
        # 옵션을 받아 유연하게 설정 가능하도록 변경
        self.detector = FER(mtcnn=use_mtcnn)
    
    def analyze(self, image_input):
        """
        이미지에서 감정을 분석합니다.
        :param image_input: 파일 경로(str) 또는 이미지 배열(numpy.ndarray)
        """
        img = None

        # 1. 입력 타입에 따른 이미지 로드 처리
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {image_input}")
            
            # 한글 경로 지원을 위한 처리 (cv2.imread는 한글 경로에서 종종 실패함)
            img = cv2.imdecode(np.fromfile(image_input, dtype=np.uint8), cv2.IMREAD_COLOR)
        
        elif isinstance(image_input, np.ndarray):
            img = image_input
        
        else:
            raise TypeError("이미지 경로나 numpy 배열(이미지 데이터)만 입력 가능합니다.")

        if img is None:
            raise ValueError("이미지를 읽을 수 없습니다.")

        # 2. 감정 분석 수행
        result = self.detector.detect_emotions(img)

        if not result:
            return {'status': 'fail', 'message': '얼굴이 감지되지 않았습니다.'}
        
        # 3. 주요 얼굴 추출 (여러 명일 경우 가장 bounding box가 큰 얼굴 선택)
        # 단순히 0번째를 가져오는 것보다, 가장 확실한 얼굴을 가져오는 것이 안전함
        top_face = max(result, key=lambda x: x['box'][2] * x['box'][3]) 
        
        emotions = top_face['emotions']
        dominant_emotion = max(emotions, key=emotions.get)

        return {
            'status': 'success',
            'emotion': dominant_emotion,
            'confidence': emotions[dominant_emotion],
            'detail': emotions,
            'box': top_face['box'] # 얼굴 위치 정보도 같이 주면 활용도가 높음
        }

# --- 테스트 코드 (사용 예시) ---
if __name__ == "__main__":
    # 라이브러리 내부 테스트 시에는 이렇게 보호해주는 것이 관례입니다.
    
    try:
        analyzer = EmotionAnalyzer(use_mtcnn=True)
        
        # 경로로 테스트
        result = analyzer.analyze('test.jpg')
        print(f"분석 결과: {result}")

    except Exception as e:
        print(f"에러 발생: {e}")