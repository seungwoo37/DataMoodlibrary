# cli.py
import argparse
from pathlib import Path

from datamood import MoodSorter
from datamood.utils import iter_input_files


def main() -> None:
    """datamood 명령행 인터페이스의 엔트리 포인트."""


    parser = argparse.ArgumentParser(
        prog="datamood",
        description="텍스트 / 오디오 파일 또는 YouTube URL을 감정 레이블별로 분석/정렬하는 CLI",
    )


    # 파일/폴더 입력(선택적 — YouTube 모드이면 없어도 됨)
    parser.add_argument(
        "input",
        nargs="?",
        help="입력 파일 또는 디렉토리 경로 (YouTube URL 모드에서는 생략 가능)",
    )

    # YouTube URL 분석 기능 추가
    parser.add_argument(
        "--youtube",
        help="YouTube URL에서 오디오를 추출하여 감정 분석",
    )

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

    sorter = MoodSorter()

    # -----------------------------
    #   YouTube 분석 모드
    # -----------------------------
    if args.youtube:
        print(f"[INFO] YouTube URL 분석 시작: {args.youtube}")
        result = sorter.analyze_youtube(args.youtube)
        print(
            f"[YouTube] {result['url']} -> {result['emotion_label']}\n"
            f"인식된 텍스트 일부: {result['raw'].get('recognized_text', '')[:50]}..."
        )
        return

    # YouTube가 아닌 경우 input은 필수
    if not args.input:
        parser.error("input 경로 또는 --youtube 중 하나는 반드시 지정해야 합니다.")

    input_path = Path(args.input)
    output_root = Path(args.output)

    # -----------------------------
    #   파일 정렬 모드
    # -----------------------------
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