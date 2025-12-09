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

    # ------------------ 공개 API: 분석만 ------------------ #

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
        extracted_text: Optional[str] = self.youtube_downloader.extract_text_from_youtube(
            url
        )

        if not extracted_text:
            # STT 실패 등
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
            extracted_text: Optional[str] = self.audio_preprocessor.extract_text_from_audio(
                str(p)
            )

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
        # 같은 이름 있으면 _1, _2 붙여서 계속 누적
        dst = make_unique_path(dst)

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
            # 1-1) 유튜브 URL이면 (watch / youtu.be / shorts 다 포함)
            if (
                "youtube.com/watch" in input_value
                or "youtu.be/" in input_value
                or "youtube.com/shorts" in input_value
            ):
                return self.analyze_youtube(input_value)
            # 1-2) 그 외 http(s) URL → 기사 URL이라고 보고 처리
            else:
                url_result = self.text_analyzer.analyze_url(input_value)
                # {"title": ..., "analysis": {...}, "text": ...} 가 온다고 가정
                label = self._label_from_text_result(url_result)

                return {
                    "type": "url",
                    "url": input_value,
                    "emotion_label": label,
                    "raw": url_result,
                }

        # 2) URL이 아니면 → 로컬 파일로 간주
        return self.analyze_file(input_value)

    # ------------------ 공개 API: 분석 + 저장/정렬 ------------------ #

    def analyze_and_sort(
        self,
        input_value: str | Path,
        base_dir: str | Path,
        move: bool = False,
    ) -> Dict[str, Any]:
        """
        입력 하나(텍스트/오디오 파일 또는 URL)를 받아서:

        1) self.analyze()로 감정 분석
        2) 로컬 파일이면 그대로 sorted/<label>/ 로 정렬
        3) YouTube URL이면 recognized_text를 .txt로 저장 후 정렬
        4) 기사 URL이면 본문 text를 .txt로 저장 후 정렬
        """
        base_dir = Path(base_dir)
        downloaded_dir = base_dir / "downloaded"
        youtube_txt_dir = downloaded_dir / "youtube"
        article_txt_dir = downloaded_dir / "articles"
        output_root = base_dir / "sorted"

        # 폴더 생성 (있으면 그대로 사용)
        youtube_txt_dir.mkdir(parents=True, exist_ok=True)
        article_txt_dir.mkdir(parents=True, exist_ok=True)
        output_root.mkdir(parents=True, exist_ok=True)

        # 1) 공통 분석
        result = self.analyze(input_value)
        input_type = result.get("type")

        result.setdefault("saved_txt_path", None)
        result.setdefault("sorted_path", None)
        result.setdefault("moved", False)

        # 2-1) 로컬 텍스트/오디오 파일
        if input_type in ("text", "audio"):
            src_path = result.get("path")
            if src_path:
                sort_result = self.sort_file(src_path, output_root, move=move)
                result["sorted_path"] = sort_result.get("sorted_path")
                result["moved"] = sort_result.get("moved", False)
            return result

        # 2-2) YouTube URL → recognized_text 저장 후 정렬
        if input_type == "youtube":
            raw = result.get("raw") or {}
            recognized = raw.get("recognized_text")
            url = result.get("url", "youtube")
            vid_id = safe_filename(url.split("/")[-1] or "youtube")

            # 🔹 STT가 실패해도, 에러 메시지라도 텍스트로 저장
            if not recognized:
                recognized = f"[STT 실패: {raw.get('error', 'no_text')}]"

            txt_path = youtube_txt_dir / f"youtube_{vid_id}.txt"
            txt_path = make_unique_path(txt_path)  # 이미 있으면 _1, _2 붙이기
            txt_path.write_text(recognized, encoding="utf-8")

            sort_result = self.sort_file(txt_path, output_root, move=move)
            result["saved_txt_path"] = str(txt_path)
            result["sorted_path"] = sort_result.get("sorted_path")
            result["moved"] = sort_result.get("moved", False)
            return result


        # 2-3) 기사 URL → 본문 텍스트 저장 후 정렬
        if input_type == "url":
            raw = result.get("raw") or {}
            article_text = raw.get("text")
            title = raw.get("title") or "article"

            if not article_text:
                return result  # 본문이 없으면 저장/정렬 불가

            safe_title = safe_filename(title)
            txt_path = article_txt_dir / f"{safe_title}.txt"
            txt_path = make_unique_path(txt_path)
            txt_path.write_text(article_text, encoding="utf-8")

            sort_result = self.sort_file(txt_path, output_root, move=move)
            result["saved_txt_path"] = str(txt_path)
            result["sorted_path"] = sort_result.get("sorted_path")
            result["moved"] = sort_result.get("moved", False)
            return result

        # 그 외 타입은 그냥 분석 결과만 반환
        return result


# ------------------ 유틸 함수들 ------------------ #

def is_http_url(s: str) -> bool:
    return isinstance(s, str) and (s.startswith("http://") or s.startswith("https://"))


def safe_filename(name: str) -> str:
    """
    파일 이름에 못 들어가는 문자들을 '_' 로 치환해주는 유틸.
    URL, 기사 제목 등을 파일 이름으로 쓸 때 사용한다.
    """
    cleaned = []
    for ch in name:
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in ("-", "_", "."):
            cleaned.append(ch)
        else:
            cleaned.append("_")
    return "".join(cleaned) or "untitled"


def make_unique_path(path: Path) -> Path:
    """
    이미 같은 이름의 파일이 있으면
    filename.txt → filename_1.txt, filename_2.txt ... 식으로
    겹치지 않는 경로를 만들어준다.
    """
    path = Path(path)
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1
