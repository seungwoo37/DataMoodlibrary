# datamood/mood_sorter.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional

from datamood.audio import AudioPreprocessor
from datamood.image import EmotionAnalyzer
from datamood.text import EmphaticSentimentAnalyzer
from datamood.utils import (
    get_file_type,
    build_output_path,
    move_or_copy,
)


class MoodSorter:
    """
    텍스트 / 이미지 / 오디오 파일을 받아서
    - 공통 감정 레이블(label)로 분류하고
    - 필요하면 폴더로 정리까지 해주는 헬퍼 클래스.
    """

    def __init__(self, language: str = "ko-KR"):
        self.audio_preprocessor = AudioPreprocessor(language=language)
        self.image_analyzer = EmotionAnalyzer()
        self.text_analyzer = EmphaticSentimentAnalyzer()

    # ------------------ 내부 헬퍼 ------------------ #

    def _label_from_text_result(self, result: Dict[str, Any]) -> str:
        """
        EmphaticSentimentAnalyzer.analyze() 결과에서 최종 레이블만 뽑는다.
        결과는 이미 '강한 긍정/긍정/중립/부정/강한 부정' 으로 나와 있으니 그대로 사용.
        """
        return result.get("label", "중립")

    def _label_from_image_result(self, result: Dict[str, Any]) -> str:
        """
        FER 결과에서 emotion 값을 보고 간단히 긍/부/중립을 정한다.
        fer 라이브러리의 기본 감정: angry, disgust, fear, happy, sad, surprise, neutral
        """
        emotion = result.get("emotion")
        if emotion is None:
            # 예: 얼굴이 감지되지 않았을 때
            return "중립"

        negative = {"angry", "disgust", "fear", "sad"}
        positive = {"happy", "surprise"}

        if emotion in positive:
            return "긍정"
        if emotion in negative:
            return "부정"
        return "중립"

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

    def analyze_file(self, path: str | Path) -> Dict[str, Any]:
        """
        파일 하나(txt / 이미지 / 오디오)를 받고 감정 분석 결과를 반환.
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

        elif file_type == "image":
            image_result = self.image_analyzer.analyze(str(p))
            label = self._label_from_image_result(image_result)

            return {
                "path": str(p),
                "type": "image",
                "emotion_label": label,
                "raw": image_result,
            }

        elif file_type == "audio":
            # 1) 오디오 → 텍스트
            extracted_text: Optional[str] = self.audio_preprocessor.extract_text_from_audio(
                str(p)
            )

            if not extracted_text:
                # 인식 실패한 경우, '중립'으로 처리하거나 필요시 "인식 실패" 레이블도 가능
                return {
                    "path": str(p),
                    "type": "audio",
                    "emotion_label": "중립",
                    "raw": {"error": "audio_recognition_failed"},
                }

            # 2) 텍스트 감정 분석 재사용
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
            return {
                "path": str(p),
                "type": "unknown",
                "emotion_label": "unknown",
                "raw": {},
            }

    def sort_file(self, path: str | Path, output_root: str | Path, move: bool = False) -> Dict[str, Any]:
        """
        파일 하나를 분석해서,
        output_root/레벨/파일명 으로 복사(또는 이동)한다.
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
