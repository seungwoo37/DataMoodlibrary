# datamood/mood_sorter.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional

from .audio import AudioPreprocessor, YouTubeDownloader
from .text import EmphaticSentimentAnalyzer
from .utils import get_file_type, build_output_path, move_or_copy


class MoodSorter:
    """
    텍스트 / 오디오 파일(그리고 YouTube URL)을 받아서
    - 감정 레이블(label)을 산출하고
    - 필요하면 폴더로 정리까지 해주는 헬퍼 클래스.
    """

    def __init__(self, language: str = "ko-KR"):
        # 오디오(파일) → 텍스트
        self.audio_preprocessor = AudioPreprocessor(language=language)
        # YouTube URL → 오디오 다운로드 → 텍스트
        self.youtube_downloader = YouTubeDownloader()
        # 텍스트 감정 분석기
        self.text_analyzer = EmphaticSentimentAnalyzer()

    # ------------------ 내부 헬퍼 ------------------ #

    def _label_from_text_result(self, result: Dict[str, Any]) -> str:
        """
        EmphaticSentimentAnalyzer.analyze() 결과에서 최종 레이블만 뽑는다.
        결과는 '매우 긍정적/긍정적/중립적/부정적/매우 부정적' 등.
        """
        return result.get("label", "중립")

    # ------------------ 공개 API ------------------ #

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        순수 텍스트 문자열 하나에 대해 감정을 분석한다.
        """
        text_result = self.text_analyzer.analyze(text)
        label = self._label_from_text_result(text_result)

        return {
            "type": "text",
            "original": text,
            "emotion_label": label,
            "raw": text_result,
        }

    def analyze_youtube(self, url: str) -> Dict[str, Any]:
        """
        YouTube URL 오디오를 다운로드 → 텍스트 인식 → 감정 분석한다.
        """
        # 🔧 핵심: YouTubeDownloader에 구현된 extract_text_from_youtube 사용
        extracted_text: Optional[str] = self.youtube_downloader.extract_text_from_youtube(url)

        if not extracted_text:
            return {
                "type": "youtube",
                "url": url,
                "emotion_label": "중립",
                "raw": {"error": "audio_recognition_failed"},
            }

        text_result = self.text_analyzer.analyze(extracted_text)
        label = self._label_from_text_result(text_result)

        return {
            "type": "youtube",
            "url": url,
            "emotion_label": label,
            "raw": {
                "recognized_text": extracted_text,
                "text_analysis": text_result,
            },
        }

    def analyze_file(self, path: str | Path) -> Dict[str, Any]:
        """
        파일 하나(txt / 오디오)를 받고 감정 분석 결과를 반환한다.
        """
        p = Path(path)
        file_type = get_file_type(p)

        if file_type == "text":
            text = p.read_text(encoding="utf-8")
            text_result = self.text_analyzer.analyze(text)
            label = self._label_from_text_result(text_result)

            return {
                "path": str(p),
                "type": "text",
                "emotion_label": label,
                "raw": text_result,
            }

        elif file_type == "audio":
            # 1) 오디오 → 텍스트
            extracted_text: Optional[str] = self.audio_preprocessor.extract_text_from_audio(str(p))

            if not extracted_text:
                return {
                    "path": str(p),
                    "type": "audio",
                    "emotion_label": "중립",
                    "raw": {"error": "audio_recognition_failed"},
                }

            # 2) 텍스트 감정 분석
            text_result = self.text_analyzer.analyze(extracted_text)
            label = self._label_from_text_result(text_result)

            return {
                "path": str(p),
                "type": "audio",
                "emotion_label": label,
                "raw": {
                    "recognized_text": extracted_text,
                    "text_analysis": text_result,
                },
            }

        else:
            # 지원하지 않는 타입
            return {
                "path": str(p),
                "type": "unknown",
                "emotion_label": "unknown",
                "raw": {},
            }

    def sort_file(
        self,
        path: str | Path,
        output_root: str | Path,
        move: bool = False,
    ) -> Dict[str, Any]:
        """
        파일 하나를 분석해서,
        output_root/감정_레이블/파일명 으로 복사(또는 이동)한다.
        """
        p = Path(path)
        output_root = Path(output_root)

        result = self.analyze_file(p)
        label = result.get("emotion_label", "unknown")

        dst = build_output_path(output_root, label, p)
        move_or_copy(p, dst, move=move)

        result["sorted_path"] = str(dst)
        result["moved"] = bool(move)
        return result
    def analyze(self, input_value: str | Path) -> Dict[str, Any]:
        """
        만능 분석 함수:
        - YouTube URL  → analyze_youtube()
        - 일반 http(s) URL(기사 등) → text_analyzer.analyze_url()
        - 그 외(로컬 파일 경로) → analyze_file()
        """
        # 1) 문자열이면서 URL인 경우
        if isinstance(input_value, str) and is_http_url(input_value):
            # 1-1) 유튜브 URL이면
            if "youtube.com/watch" in input_value or "youtu.be/" in input_value:
                return self.analyze_youtube(input_value)
            # 1-2) 그 외 http(s) URL → 기사 URL이라고 보고 처리
            else:
                url_result = self.text_analyzer.analyze_url(input_value)
                # EmphaticSentimentAnalyzer.analyze_url() 이
                # {"title": ..., "analysis": {...}, "text": ...} 이런 식으로
                # 리턴한다고 가정하고 레이블만 뽑아준다.
                label = self._label_from_text_result(url_result)

                return {
                    "type": "url",
                    "url": input_value,
                    "emotion_label": label,
                    "raw": url_result,
                }

        # 2) URL이 아니면 → 로컬 파일로 간주
        return self.analyze_file(input_value)

def is_http_url(s: str) -> bool:
    return isinstance(s, str) and (s.startswith("http://") or s.startswith("https://"))
