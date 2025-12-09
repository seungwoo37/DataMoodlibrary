# DataMoodlibrary/main_runner.py

# DataMoodlibrary.datamood.audio 모듈에서 YouTubeDownloader 클래스를 import 합니다.
# 파일 경로: datamood/audio/audio_mood.py
from DataMoodlibrary.datamood.audio.audio_mood import YouTubeDownloader 

def run_processing(url):
    """
    YouTube URL을 받아 텍스트 추출 파이프라인을 실행하는 함수
    """
    
    print("--- [MAIN RUNNER] YouTube 오디오 텍스트 추출 프로그램 시작 ---")
    
    # 1. YouTubeDownloader 객체 초기화
    # 임시 파일을 저장할 디렉토리와 최종 텍스트 파일 이름 지정
    output_txt_file = r"c:\Users\jinui\Downloads\new_txt"
    downloader = YouTubeDownloader(output_dir="temp_youtube_data")
    
    try:
        # 2. 통합 실행 함수 호출
        recognized_text = downloader.extract_text_from_youtube(
            youtube_url=url, 
            cleanup=True, 
            output_txt_path=output_txt_file
        )

        # 3. 결과 출력
        if recognized_text:
            print("\n========================================")
            print("✅ [MAIN RUNNER] 최종 인식된 텍스트 확인 완료.")
            print(f"✅ 전체 텍스트가 '{output_txt_file}'에 저장되었습니다.")
            print("========================================")
        else:
            print("\n❌ [MAIN RUNNER] 텍스트 인식에 실패했거나 내용이 없습니다.")

    except Exception as e:
        print(f"\n🚨 [MAIN RUNNER] 프로그램 실행 중 치명적인 오류 발생: {e}")

# --- 실행 부분 ---
if __name__ == "__main__":
    # 🚨 여기에 테스트할 실제 YouTube URL을 입력하세요.
    YOUTUBE_URL_TO_PROCESS = "https://www.youtube.com/watch?v=QMOsAtTA2n0" 
    
    if YOUTUBE_URL_TO_PROCESS == "YOUR_YOUTUBE_URL_HERE":
        print("경고: 실행을 위해 YOUTUBE_URL_TO_PROCESS 변수에 유효한 URL을 입력해야 합니다.")
    else:
        # main_runner.py가 DataMoodlibrary 폴더 내부에서 실행되어야 상대경로 import가 원활합니다.
        run_processing(YOUTUBE_URL_TO_PROCESS)