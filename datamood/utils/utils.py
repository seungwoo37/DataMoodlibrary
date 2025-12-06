# datamood/utils/utils.py
from pathlib import Path
import shutil
from typing import Iterable, Literal

# 텍스트 파일 확장자
TEXT_EXT = {".txt"}

# 오디오 파일 확장자 (SpeechRecognition AudioFile이 안전하게 처리할 수 있는 확장자들)
AUDIO_EXT = {".wav", ".flac", ".aiff", ".aif"}


def get_file_type(path: Path) -> Literal["text", "audio", "unknown"]:
    """파일 확장자를 보고 타입을 판별한다."""
    ext = path.suffix.lower()

    if ext in TEXT_EXT:
        return "text"
    if ext in AUDIO_EXT:
        return "audio"

    # 이미지 기능을 제거했기 때문에 image는 더 이상 반환하지 않음
    return "unknown"


def iter_input_files(input_path: Path) -> Iterable[Path]:
    """
    단일 파일이면 그대로 반환,
    디렉토리면 재귀적으로 내부 모든 파일을 순회한다.
    """
    if input_path.is_file():
        yield input_path
        return

    if input_path.is_dir():
        for p in sorted(input_path.rglob("*")):
            if p.is_file():
                yield p


def ensure_dir(path: Path) -> None:
    """디렉토리가 없다면 생성."""
    path.mkdir(parents=True, exist_ok=True)


def build_output_path(output_root: Path, label: str, src: Path) -> Path:
    """
    감정 레이블(label) 기준으로 하위 폴더를 만들고,
    원본 파일 이름을 그대로 유지한 경로를 반환한다.

    ex) output_root/긍정/파일이름.txt
    """
    safe_label = label.replace("/", "_")  # 혹시 모를 슬래시 처리
    return output_root / safe_label / src.name


def move_or_copy(src: Path, dst: Path, move: bool = False) -> None:
    """move=True면 이동, 아니면 복사."""
    ensure_dir(dst.parent)

    if move:
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(str(src), str(dst))
