import speech_recognition as sr

class AudioPreprocessor:
    """
    오디오 파일에서 텍스트를 추출하여 감정 분석을 위한
    텍스트 전처리 단계를 수행하고, 그 결과를 파일로 저장하는 클래스입니다.
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

    def save_text_to_file(self, text_content, output_file_path):
        """
        추출된 텍스트를 지정된 경로의 .txt 파일로 저장합니다.
        
        :param text_content: 저장할 텍스트 문자열
        :param output_file_path: 저장할 .txt 파일의 경로 및 이름
        """
        try:
            # 'w' 모드(쓰기 모드)와 인코딩(UTF-8)을 지정하여 파일 열기
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"💾 텍스트 저장 성공: 파일 '{output_file_path}'에 저장되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 파일 저장 오류 발생: {e}")
            return False


# ----------------------------------------------------------------------
# --- 예시 사용 ---
if __name__ == "__main__":
    # 인식 테스트를 위해 실제 오디오 파일 경로로 대체해야 합니다.
    example_audio_path = r"C:\Users\jinui\Downloads\안녕하세오.wav"
    # 텍스트를 저장할 경로와 파일명을 지정합니다. (예: 현재 디렉토리의 'recognized_speech.txt')
    output_text_path = "recognized_speech.txt"
    
    preprocessor = AudioPreprocessor(language='ko-KR')
    
    # 1. 텍스트 추출
    recognized_text = preprocessor.extract_text_from_audio(example_audio_path)
    
    if recognized_text:
        print("\n[다음 단계: 텍스트 파일 저장]")
        # 2. 추출된 텍스트를 파일로 저장
        preprocessor.save_text_to_file(recognized_text, output_text_path)
        
        # 3. 다음 감정 분석 전처리 단계 안내
        print("\n[이후 파이프라인]")
        print("이제 저장된 텍스트를 토크나이징, 정규화 등의 텍스트 전처리 파이프라인으로 전달하여 감정을 분석합니다.")