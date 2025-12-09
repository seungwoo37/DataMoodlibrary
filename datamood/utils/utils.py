# datamood/utils/utils.py
from pathlib import Path
import shutil
from typing import Iterable, Literal

# 텍스트 파일 확장자
TEXT_EXT = {".txt"}

# 오디오 파일 확장자 (SpeechRecognition AudioFile이 안전하게 처리할 수 있는 확장자들)
AUDIO_EXT = {".wav", ".flac", ".aiff", ".aif"}


def get_file_type(path: Path) -> Literal["text", "audio", "unknown"]:
    """
    파일 확장자를 기반으로 입력 파일의 타입(text/audio/unknown)을 판별한다.

    Parameters
    ----------
    path : Path
        타입을 판별할 파일 경로 객체.

    Returns
    -------
    Literal["text", "audio", "unknown"]
        - "text": 텍스트 파일(.txt)
        - "audio": 오디오 파일(.wav, .flac, .aiff, .aif)
        - "unknown": 위 확장자에 속하지 않는 경우

    Notes
    -----
    이미지 분석 기능은 프로젝트에서 제거되었으므로
    더 이상 "image" 타입은 반환되지 않는다.

    Examples
    --------
    >>> get_file_type(Path("example.txt"))
    'text'
    >>> get_file_type(Path("sound.wav"))
    'audio'
    >>> get_file_type(Path("data.json"))
    'unknown'
    """

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
    파일 또는 디렉토리 경로를 입력받아 처리 가능한 모든 파일을 순회(iterate)한다.

    Parameters
    ----------
    input_path : Path
        단일 파일 또는 디렉토리 경로.

    Returns
    -------
    Iterable[Path]
        - 단일 파일: 해당 파일을 그대로 yield
        - 디렉토리: 내부 모든 파일을 재귀적으로 순회하여 yield

    Examples
    --------
    >>> for p in iter_input_files(Path("data/")):
    ...     print(p)
    data/a.txt
    data/sub/b.wav
    """


    if input_path.is_file():
        yield input_path
        return

    if input_path.is_dir():
        for p in sorted(input_path.rglob("*")):
            if p.is_file():
                yield p


def ensure_dir(path: Path) -> None:
    """
    지정된 경로에 디렉토리가 없으면 생성한다.

    Parameters
    ----------
    path : Path
        생성할 디렉토리 경로.

    Returns
    -------
    None

    Examples
    --------
    >>> ensure_dir(Path("output/logs"))
    # 디렉토리가 존재하지 않을 경우 생성됨
    """

    """디렉토리가 없다면 생성."""
    path.mkdir(parents=True, exist_ok=True)


def build_output_path(output_root: Path, label: str, src: Path) -> Path:
    """
    감정 레이블(label) 별로 하위 폴더를 구성하고,
    원본 파일명을 유지한 새로운 출력 경로를 생성한다.

    Parameters
    ----------
    output_root : Path
        정리된 결과를 저장할 최상위 폴더 경로.
    label : str
        감정 레이블 (예: "positive", "negative").
    src : Path
        원본 파일 경로.

    Returns
    -------
    Path
        output_root/label/원본파일명 형식의 새 파일 경로.

    Examples
    --------
    >>> build_output_path(Path("output"), "positive", Path("a.txt"))
    PosixPath('output/positive/a.txt')
    """

    safe_label = label.replace("/", "_")  # 혹시 모를 슬래시 처리
    return output_root / safe_label / src.name


def move_or_copy(src: Path, dst: Path, move: bool = False) -> None:
    """
    파일을 지정된 위치로 이동하거나 복사한다.

    Parameters
    ----------
    src : Path
        원본 파일 경로.
    dst : Path
        이동 또는 복사될 대상 파일 경로.
    move : bool, optional
        True이면 파일을 이동(shutil.move),
        False이면 복사(shutil.copy2). 기본값은 False.

    Returns
    -------
    None

    Examples
    --------
    >>> move_or_copy(Path("a.txt"), Path("backup/a.txt"), move=False)
    # 파일이 backup/a.txt 로 복사됨

    >>> move_or_copy(Path("a.txt"), Path("archive/a.txt"), move=True)
    # 파일이 archive/a.txt 로 이동됨
    """

    ensure_dir(dst.parent)

    if move:
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(str(src), str(dst))
