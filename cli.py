# cli.py
import argparse
from pathlib import Path

from datamood import MoodSorter
from datamood.utils import iter_input_files


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="datamood",
        description="텍스트 / 이미지 / 오디오 파일을 감정 레이블별로 자동 정렬하는 CLI",
    )
    parser.add_argument("input", help="입력 파일 또는 디렉토리 경로")
    parser.add_argument(
        "-o",
        "--output",
        default="sorted",
        help="정렬된 파일을 저장할 루트 디렉토리 (기본: ./sorted)",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="복사 대신 파일을 이동시키기 (기본: 복사)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_root = Path(args.output)

    sorter = MoodSorter()

    files = list(iter_input_files(input_path))
    if not files:
        print(f"[WARN] 입력 경로에서 파일을 찾지 못했습니다: {input_path}")
        return

    print(f"총 {len(files)}개 파일 처리 시작...")

    for p in files:
        result = sorter.sort_file(p, output_root, move=args.move)
        print(
            f"[{result['type']}] {p.name} -> {result['emotion_label']} "
            f"({result['sorted_path']})"
        )


if __name__ == "__main__":
    main()
