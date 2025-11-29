import speech_recognition as sr

class AudioPreprocessor:
    """
    오디오 파일에서 텍스트를 추출하여 감정 분석을 위한
    텍스트 전처리 단계를 수행하는 클래스입니다.
    """
    def __init__(self, language='ko-KR'):
        # Recognizer 객체 초기화
        self.recognizer = sr.Recognizer()
        # 음성 인식 언어 설정 (기본값: 한국어)
        self.language = language

    def extract_text_from_audio(self, audio_file_path):
        """
        주어진 오디오 파일 경로에서 텍스트를 추출합니다.
        
        :param audio_file_path: 인식할 오디오 파일의 경로 (wav, aiff, flac 등)
        :return: 인식된 텍스트 문자열 또는 인식 실패 시 None
        """
        try:
            # 오디오 파일을 음원(source)으로 지정
            with sr.AudioFile(audio_file_path) as source:
                print(f"-> 오디오 파일 '{audio_file_path}' 로드 중...")
                
                # 파일 전체를 오디오 데이터로 읽어 들임
                audio_data = self.recognizer.record(source)
                
            print("-> 음성 인식을 시도합니다...")
            
            # Google Web Speech API를 사용하여 텍스트로 변환
            # key 매개변수를 생략하면 무료 공용 키를 사용합니다.
            text = self.recognizer.recognize_google(
                audio_data, 
                language=self.language
            )
            
            print(f"✅ 인식 성공: '{text[:50]}...'")
            return text
            
        except sr.UnknownValueError:
            print("❌ 인식 실패: 음성을 이해할 수 없거나 명확하지 않습니다.")
            return None
        except sr.RequestError as e:
            print(f"❌ 요청 오류: Google API 연결 문제 발생; {e}")
            return None
        except FileNotFoundError:
            print(f"❌ 파일 오류: 지정된 파일 '{audio_file_path}'을 찾을 수 없습니다.")
            return None
        except Exception as e:
            print(f"❌ 기타 오류 발생: {e}")
            return None


# --- 예시 사용 ---
if __name__ == "__main__":
    # 라이브러리 설치 필요: pip install SpeechRecognition
    # 인식 테스트를 위해 실제 오디오 파일 경로로 대체해야 합니다.
    example_audio_path = r"C:\Users\jinui\Downloads\안녕하세오.wav"
    
    # 더 정확한 테스트를 위해 유효한 wav 파일을 준비해야 합니다.
    # 이 코드를 실행하기 전에 'sample_korean_speech.wav' 파일을 해당 경로에 두거나, 
    # 유효한 경로로 변경해야 합니다.
    
    preprocessor = AudioPreprocessor(language='ko-KR')
    
    recognized_text = preprocessor.extract_text_from_audio(example_audio_path)
    
    if recognized_text:
        # 추출된 텍스트를 이용해 다음 감정 분석 전처리를 수행
        print("\n[다음 단계]")
        print(f"추출된 텍스트: '{recognized_text}'")
        print("이제 이 텍스트를 토크나이징, 정규화 등의 텍스트 전처리 파이프라인으로 전달하여 감정을 분석합니다.")