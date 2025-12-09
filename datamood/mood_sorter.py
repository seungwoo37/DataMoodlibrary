from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional

from .audio import AudioPreprocessor, YouTubeDownloader
from .text import EmphaticSentimentAnalyzer
from .utils import get_file_type, build_output_path, move_or_copy

class MoodSorter:
    """
    텍스트 / 오디오 파일 또는 YouTube URL을 받아 감정 분석을 도와주는 헬퍼 클래스.

    이 클래스는 내부적으로 다음 컴포넌트를 사용한다.

    - ``AudioPreprocessor``: 오디오 파일을 텍스트로 변환
    - ``YouTubeDownloader``: YouTube URL에서 오디오를 추출하고 텍스트로 변환
    - ``EmphaticSentimentAnalyzer``: 텍스트 감정 분석
    """

    def __init__(self, language: str = "ko-KR"):
        """
        MoodSorter 인스턴스를 초기화한다.

        Parameters
        ----------
        language : str, optional
            오디오 인식에 사용할 언어 코드.
            기본값은 "ko-KR"이며, AudioPreprocessor에 전달된다.
        """
        # 오디오(파일) → 텍스트
        self.audio_preprocessor = AudioPreprocessor(language=language)
        # YouTube URL → 오디오 다운로드 → 텍스트
        self.youtube_downloader = YouTubeDownloader()
        # 텍스트 감정 분석기
        self.text_analyzer = EmphaticSentimentAnalyzer()


    # ------------------ 내부 헬퍼 ------------------ #

    def _label_from_text_result(self, result: Dict[str, Any]) -> str:
        """
        텍스트 감성 분석 결과 딕셔너리에서 최종 감정 레이블만 추출한다.

        Parameters
        ----------
        result : dict
            EmphaticSentimentAnalyzer.analyze() 또는 analyze_url()
            등이 반환하는 감성 분석 결과 딕셔너리.

        Returns
        -------
        str
            분석 결과에서 추출한 감정 레이블.
            'label' 키가 없으면 기본값으로 "중립"을 반환한다.
        """
        return result.get("label", "중립")


    # ------------------ 공개 API: 분석만 ------------------ #

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        순수 텍스트 문자열 하나에 대해 감정 분석을 수행한다.

        Parameters
        ----------
        text : str
            분석할 텍스트 문장 또는 문단.

        Returns
        -------
        dict
            다음 정보를 포함하는 결과 딕셔너리.

            - ``type``: "text"
            - ``original``: 원본 텍스트 문자열
            - ``emotion_label``: 최종 감정 레이블(예: "positive", "negative", "중립" 등)
            - ``raw``: 내부 감정 분석기의 상세 결과 딕셔너리
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
        YouTube URL을 입력받아 오디오를 추출하고,
        음성 인식 후 텍스트 감정 분석까지 수행한다.

        Parameters
        ----------
        url : str
            분석할 YouTube 동영상의 URL.

        Returns
        -------
        dict
            다음 정보를 포함하는 결과 딕셔너리.

            - ``type``: "youtube"
            - ``url``: 입력된 YouTube URL
            - ``emotion_label``: 최종 감정 레이블 또는 "중립"(실패 시)
            - ``raw``: 인식된 텍스트, 텍스트 분석 결과, 에러 메시지 등이 포함된 딕셔너리
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
        로컬 파일 하나(txt 또는 오디오)를 입력받아 감정 분석을 수행한다.

        Parameters
        ----------
        path : str or Path
            분석할 파일 경로. 지원 확장자는 다음과 같다.

            - 텍스트: ``.txt``
            - 오디오: ``.wav``, ``.flac``, ``.aiff``, ``.aif``

        Returns
        -------
        dict
            파일 타입에 따라 다음과 같은 정보를 담는 결과 딕셔너리.

            - 텍스트 파일:
              - ``type``: "text"
              - ``path``: 파일 경로 문자열
              - ``emotion_label``: 감정 레이블
              - ``raw``: 텍스트 분석 결과
            - 오디오 파일:
              - ``type``: "audio"
              - ``path``: 파일 경로 문자열
              - ``emotion_label``: 감정 레이블 또는 "중립"(인식 실패 시)
              - ``raw``: 인식된 텍스트와 텍스트 분석 결과
            - 지원하지 않는 타입:
              - ``type``: "unknown"
              - ``emotion_label``: "unknown"
              - ``raw``: 빈 딕셔너리
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
        파일 하나를 분석한 뒤, 감정 레이블별 하위 폴더로 정리한다.

        결과 파일 경로는 대략 다음과 같은 형태가 된다.

        - output_root/<감정_레이블>/<파일명>

        Parameters
        ----------
        path : str or Path
            정렬할 원본 파일 경로.
        output_root : str or Path
            감정 레이블별로 파일을 정렬해 둘 루트 디렉터리.
        move : bool, optional
            True이면 원본 파일을 이동하고, False이면 복사한다.
            기본값은 False.

        Returns
        -------
        dict
            analyze_file()의 결과에 다음 필드가 추가된 딕셔너리.

            - sorted_path: 실제로 복사/이동된 최종 경로(문자열)
            - moved: 이동 여부(bool, move 인자와 동일)
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
        다양한 입력 타입(YouTube URL, 일반 http(s) URL, 로컬 파일)에 대해
        자동으로 적절한 분석 함수를 선택하여 감정 분석을 수행한다.

        Parameters
        ----------
        input_value : str or Path
            다음 중 하나를 받을 수 있다.

            - YouTube URL (youtube.com, youtu.be, shorts 등)
            - 일반 기사 URL (http/https)
            - 로컬 파일 경로(txt 또는 오디오 파일)

        Returns
        -------
        dict
            입력 타입에 따라 다음 형태 중 하나를 반환한다.

            - YouTube URL: analyze_youtube()의 결과
            - 기사 URL: type="url"과 분석 결과를 담은 딕셔너리
            - 로컬 파일: analyze_file()의 결과
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
        입력 하나(텍스트/오디오 파일 또는 URL)를 받아 감정 분석을 수행하고,
        필요한 경우 텍스트 파일(.txt)로 저장한 뒤 감정 레이블별 폴더로
        정렬까지 수행한다.

        동작 방식은 입력 타입별로 다음과 같다.

        - 로컬 텍스트/오디오 파일:
          - analyze()로 감정 분석을 수행한 뒤
          - base_dir/sorted/<레이블>/ 아래로 파일을 복사 또는 이동한다.
        - YouTube URL:
          - 음성을 텍스트로 변환한 결과를
            base_dir/downloaded/youtube/*.txt 로 저장한 뒤
          - base_dir/sorted/<레이블>/ 아래로 정렬한다.
        - 기사 URL(http/https):
          - 크롤링한 본문 텍스트를
            base_dir/downloaded/articles/*.txt 로 저장한 뒤
          - base_dir/sorted/<레이블>/ 아래로 정렬한다.

        Parameters
        ----------
        input_value : str or Path
            분석할 입력값(파일 경로, YouTube URL, 기사 URL 등).
        base_dir : str or Path
            다운로드된 텍스트 및 정렬된 결과를 저장할 기준 디렉터리.
        move : bool, optional
            True이면 정렬 시 원본 파일을 이동하고,
            False이면 복사한다. URL 기반 입력의 경우에는
            새로 생성된 .txt 파일만 정렬 대상이 된다.

        Returns
        -------
        dict
            self.analyze()의 결과에 다음 필드가 추가된 딕셔너리.

            - saved_txt_path: URL/YouTube에서 생성된 .txt 파일 경로(없으면 None)
            - sorted_path: 최종 정렬된 파일 경로(없으면 None)
            - moved: 이동 여부(bool)
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
    """
    주어진 문자열이 http 또는 https로 시작하는 URL 형태인지 판별한다.

    Parameters
    ----------
    s : str
        검사할 문자열.

    Returns
    -------
    bool
        문자열이 'http://' 또는 'https://'로 시작하면 True,
        그렇지 않으면 False.
    """
    return isinstance(s, str) and (s.startswith("http://") or s.startswith("https://"))



def safe_filename(name: str) -> str:
    """
    파일 이름에 사용할 수 없는 문자들을 밑줄 문자(_)로 치환하여
    안전한 파일 이름 문자열을 생성한다.

    Parameters
    ----------
    name : str
        원본 이름(예: URL, 기사 제목 등).

    Returns
    -------
    str
        파일 시스템에서 사용할 수 있는 안전한 파일 이름.
        모든 문자가 치환되어 비게 되면 "untitled"를 반환한다.
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
    이미 같은 경로의 파일이 존재하면, 뒤에 숫자 인덱스를 붙여
    겹치지 않는 고유한 경로를 만들어 준다.

    예를 들어 ``filename.txt``가 이미 있으면
    ``filename_1.txt``, ``filename_2.txt`` 순서로 새 이름을 만든다.

    Parameters
    ----------
    path : Path
        기본이 될 파일 경로.

    Returns
    -------
    Path
        아직 존재하지 않는 고유한 파일 경로.
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