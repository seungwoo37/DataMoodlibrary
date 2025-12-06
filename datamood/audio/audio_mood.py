import os 
import yt_dlp
from pydub import AudioSegment
import speech_recognition as sr
import shutil

"""
FFmpeg 환경 설정 및 경로 지정
FFmpeg은 오디오/비디오 파일을 인코딩, 디코딩, 변환하는 데 사용되는 핵심 도구
yt-dlp가 오디오를 추출하거나 pydub이 MP3를 WAV로 변환할 때 필수적으로 필요함
"""
FFMPEG_BIN_PATH = r"C:\Users\jinui\ffmpeg-2025-12-04-git-d6458f6a8b-full_build\bin" 

# 사용자 환경에 맞게 FFmpeg 실행 파일이 있는 디렉토리를 시스템 PATH 환경 변수에 추가
print(f"✅ FFmpeg 경로 설정 시도: {FFMPEG_BIN_PATH}")
os.environ["PATH"] += os.pathsep + FFMPEG_BIN_PATH
# pydub 라이브러리가 FFmpeg 실행 파일의 위치를 찾도록 환경 변수를 설정
os.environ["FFMPEG_PATH"] = os.path.join(FFMPEG_BIN_PATH, "ffmpeg.exe")
os.environ["FFPROBE_PATH"] = os.path.join(FFMPEG_BIN_PATH, "ffprobe.exe")
print(f"✅ FFMPEG_PATH 확인: {os.environ.get('FFMPEG_PATH')}")

# 오디오 파일을 받아서 텍스트로 추출하는 클래스
class AudioPreprocessor:
    """
    오디오 파일에서 텍스트를 추출하여 감정 분석을 위한
    텍스트 전처리 단계를 수행하고, 그 결과를 파일로 저장하는 클래스
    """
    def __init__(self, language='ko-KR'):
        # Recognizer 객체 초기화
        self.recognizer = sr.Recognizer()
        # 음성 인식 언어 설정 (기본값: 한국어)
        self.language = language

    def extract_text_from_audio(self, audio_file_path):
        # 주어진 오디오 파일 경로에서 텍스트를 추출
        try:
            with sr.AudioFile(audio_file_path) as source:
                print(f"-> 오디오 파일 '{audio_file_path}' 로드 중...")
                audio_data = self.recognizer.record(source)
                
            print("-> 음성 인식을 시도합니다...")
            text = self.recognizer.recognize_google(
                audio_data, 
                language=self.language
            )
            print(f"인식 성공: '{text[:50]}...'")
            return text
            
        # 인식기가 음성을 이해하지 못 했을 때
        except sr.UnknownValueError:
            print("인식 실패: 음성을 이해할 수 없거나 명확하지 않습니다.")
            return None
        # Google API 호출 시 네트워크나 인증 문제로 실패했을 때
        except sr.RequestError as e:
            print(f"요청 오류: Google API 연결 문제 발생; {e}")
            return None
        # 파일이 존재하지 않을 때
        except FileNotFoundError:
            print(f"파일 오류: 지정된 파일 '{audio_file_path}'을 찾을 수 없습니다.")
            return None
        # 그 외의 모든 예외처리
        except Exception as e:
            print(f"기타 오류 발생: {e}")
            return None

    def save_text_to_file(self, text_content, output_file_path):
        # 추출된 텍스트를 지정된 경로의 .txt 파일로 저장
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"텍스트 저장 성공: 파일 '{output_file_path}'에 저장되었습니다.")
            return True
        except Exception as e:
            print(f"파일 저장 오류 발생: {e}")
            return False


# YouTube 다운로드 및 WAV 변환 클래스
class YouTubeDownloader:
    """
    YouTube 영상에서 오디오를 다운로드하고, 음성 인식을 위해
    MP3에서 WAV 형식으로 변환하는 역할을 담당하는 클래스입니다.
    """
    def __init__(self, output_dir="audio_temp"):
        # 임시 파일을 저장할 디렉토리 이름 설정
        self.output_dir = output_dir
        # 디렉토리가 없으면 새로 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 임시 MP3 파일과 최종 WAV 파일의 경로를 정의
        self.temp_mp3_path = os.path.join(self.output_dir, "temp_audio.mp3")
        self.output_wav_path = os.path.join(self.output_dir, "output_recognition.wav")

    def download_and_convert(self, youtube_url):
        """YouTube URL에서 오디오를 다운로드하고 WAV로 변환합니다."""
        ydl_opts = {
            # yt-dlp에게 최적의 오디오 형식으로 다운로드하도록 지시
            'format': 'bestaudio/best', 
            # 다운로드된 파일의 출력 템플릿을 설정, %(ext)s는 파일 확장자
            'outtmpl': self.temp_mp3_path.replace(".mp3", ".%(ext)s"),
            # 다운로드 후 FFmpeg을 사용하여 오디오를 추출하고 MP3 코덱을 사용하도록 후처리(postprocessor)를 설정
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            # 다운로드 과정중 불필요한 정보를 걸러서 콘솔 출력을 최소화
            'quiet': True 
        }
        
        print(f"✅ 1. '{youtube_url}'에서 오디오 다운로드 및 MP3 추출 중...")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 지정된 YouTube URL에서 다운로드 실행
                ydl.download([youtube_url]) 
            
            # yt-dlp가 생성한 실제 mp3 파일 이름을 찾아 self.temp_mp3_path를 업데이트
            # 이 과정은 yt-dlp의 동작에 따라 필요할 수 있음
            for file in os.listdir(self.output_dir):
                if file.endswith(".mp3"):
                    self.temp_mp3_path = os.path.join(self.output_dir, file)
                    break

        except Exception as e:
            print(f"❌ 오디오 다운로드 중 오류 발생: {e}")
            return None
            
        print("✅ 2. 오디오를 WAV 형식으로 변환 중...")
        try:
            # pydub을 사용하여 MP3 파일을 로드
            audio = AudioSegment.from_file(self.temp_mp3_path, format="mp3")
            # 음성 인식 성능 향상을 위해 오디오를 모노(단일 채널)로 설정하고 샘플링 레이트를 16000Hz로 리샘플링(1초에 16000번 측정)
            audio = audio.set_channels(1).set_frame_rate(16000) 
            # 변환된 오디오를 WAV 형식으로 저장
            audio.export(self.output_wav_path, format="wav") 
            print(f"   -> WAV 파일 저장 완료: {self.output_wav_path}")
            return self.output_wav_path
        except Exception as e:
            print(f"❌ WAV 변환 중 오류 발생: {e}")
            return None

    def cleanup(self):
        #작업이 완료된 후 임시 디렉토리와 그 안의 파일들을 삭제하여 정리
        print("\n✅ 4. 임시 파일 정리 중...")
        try:
            # shutil.rmtree를 사용하여 디렉토리와 그 내용을 재귀적으로 삭제
            shutil.rmtree(self.output_dir)
            print(f"   -> 임시 디렉토리 ({self.output_dir}) 정리 완료.")
        except OSError as e:
            print(f"   -> 디렉토리 삭제 중 오류 발생: {e}")
            
    def extract_text_from_youtube(self, youtube_url, cleanup=True, output_txt_path = "output_transcript.txt"):
        """
        YouTube URL을 받아 오디오 다운로드 → WAV 변환 → 텍스트 인식까지 수행하는 통합 함수
        """
        print(f"YouTube URL 처리 시작: {youtube_url}")

        # 다운로드 및 변환 단계
        wav_path = self.download_and_convert(youtube_url)

        if not wav_path:
            print("❌ YouTube 오디오 처리 실패로 파이프라인 중단.")
            if cleanup:
                self.cleanup()
            return None

        # 텍스트 추출 및 저장 단계
        print("YouTube 오디오 → 텍스트 변환 시도")
        
        # AudioPreprocessor 객체 생성
        preprocessor = AudioPreprocessor(language='ko-KR') 
        
        # 생성된 객체를 통해 메서드 호출
        recognized_text = preprocessor.extract_text_from_audio(wav_path) 
        
        if recognized_text:
            preprocessor.save_text_to_file(recognized_text, output_txt_path)
            
        # 정리 단계 (생략)
        if cleanup:
            self.cleanup()

        return recognized_text
