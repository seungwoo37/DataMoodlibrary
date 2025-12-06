# datamood/text/text_mood.py
from konlpy.tag import Okt


class MorphSentimentAnalyzer:
    """
    형태소 분석(Okt) + 간단한 lexicon + 부정어/강조어/TF-IDF 개념을 이용한 감성 분석기.
    """

    def __init__(self):
        self.okt = Okt()  # 형태소 분석기 로드

        # 감성 사전
        self.lexicon = {
            # 긍정 (최대 +2)
            "좋다": 1, "최고다": 2, "훌륭하다": 2, "추천하다": 1, "감동하다": 1,
            "행복하다": 2, "만족하다": 1, "예쁘다": 1, "빠르다": 1, "친절하다": 1,
            "성공하다": 1, "대박이다": 2, "귀엽다": 1, "아름답다": 1, "가뿐하다": 1,
            "감개무량하다": 1, "감격하다": 1, "감미롭다": 1, "감복하다": 1, "감사하다": 1,
            "경이롭다": 1, "경쾌하다": 1, "고맙다": 1,
            "재미있다": 2, "감동": 1, "대박": 2,

            # 부정 (최소 -2)
            "싫다": -1, "나쁘다": -1, "최악이다": -2, "별로다": -1, "실망하다": -2,
            "느리다": -1, "비싸다": -1, "불친절하다": -2, "짜증나다": -1,
            "아쉽다": -1, "어렵다": -1, "지저분하다": -1, "가관이다": -2,
            "가련하다": -1, "가소롭다": -1, "가슴아프다": -2, "가엾다": -1,
            "각박하다": -1, "간절하다": -1, "갑갑하다": -1, "거북하다": -1,
            "걱정하다": -1, "겁나다": -1, "격노하다": -2, "격분하다": -2,
            "고달프다": -1, "고독하다": -2, "고통스럽다": -1, "최악": -2, "별로": -1,
        }

        # TF-IDF 개념 적용 (가중치)
        self.idf_weights = {
            # 높은 가중치 (감성 핵심어)
            "최고다": 2.0, "최악이다": 2.0, "대박이다": 1.8, "재미있다": 1.8,
            "훌륭하다": 1.7, "실망하다": 1.7,
            "좋다": 1.5, "나쁘다": 1.5, "감동하다": 1.5, "비싸다": 1.5,
            "불친절하다": 1.5, "짜증나다": 1.5,
            "감동": 1.5, "대박": 1.8, "최악": 2.0,

            # 중간 가중치
            "싫다": 1.0, "만족하다": 1.0, "빠르다": 1.0, "느리다": 1.0,

            # 낮은 가중치 (자주 쓰이는 일반어)
            "영화": 0.8, "서비스": 0.8, "가격": 0.8, "품질": 0.8,
            "배우": 0.8, "연기": 0.8, "것": 0.5, "같다": 0.5,
        }

        # 부정어, 강조어
        self.negators = ["안", "않다", "못", "없다", "아니다"]
        self.intensifiers = ["진짜", "정말", "매우", "완전", "너무", "엄청", "겁나", "가장"]

    def text_analyze(self, text: str):
        """
        입력 텍스트 한 덩어리를 분석하여 dict 형태로 결과 반환.
        """
        if not text or text.isspace():
            return {
                "text": text,
                "tokens": [],
                "label": "빈 텍스트",
                "score": 0.0,
                "percentage": "50.00%",
                "reason": [],
            }

        # 형태소 분석 및 TF 계산
        tokens = self.okt.morphs(text, stem=True)
        tf_count = {}
        for token in tokens:
            tf_count[token] = tf_count.get(token, 0) + 1

        total_score = 0.0
        details = []

        sentiment_words = [token for token in tokens if token in self.lexicon]
        num_sentiment_words = len(sentiment_words)

        MAX_POSSIBLE_SCORE = num_sentiment_words * 4
        MIN_POSSIBLE_SCORE = num_sentiment_words * -4

        if num_sentiment_words == 0:
            percentage = 50.0
            label = "중립"
        else:
            for i, token in enumerate(tokens):
                if token in self.lexicon:
                    base_score = self.lexicon[token]
                    current_score = float(base_score)

                    idf_weight = self.idf_weights.get(token, 1.0)
                    tf = tf_count[token]
                    weighted_score_multiplier = tf * idf_weight

                    current_score *= weighted_score_multiplier
                    msg_parts = [f"'{token}'({base_score}*TF{tf}*IDF{idf_weight:.1f})"]

                    # 문맥(앞뒤 2~3 토큰) 추출
                    context_before = tokens[max(0, i - 2):i]
                    context_after = tokens[i + 1:min(len(tokens), i + 3)]
                    context_tokens = context_before + context_after

                    # 부정어 있으면 반전
                    if any(neg in context_tokens for neg in self.negators):
                        current_score = -current_score
                        msg_parts.append(" + 부정어(반전)")

                    # 강조어 있으면 점수 2배
                    if any(inten in context_tokens for inten in self.intensifiers):
                        current_score *= 2
                        msg_parts.append(" + 강조어(x2)")

                    total_score += current_score
                    details.append(f"{''.join(msg_parts)} (최종: {current_score:+.2f})")

            # 전체 문장에 부정어 있으면 긍정 점수 0.9배 약화
            if any(neg in tokens for neg in self.negators):
                if total_score > 0:
                    total_score *= 0.9
                    details.append(">> 전체 부정어 감지: 긍정 점수 0.9배 약화")

            # 점수 정규화
            range_of_scores = MAX_POSSIBLE_SCORE - MIN_POSSIBLE_SCORE
            if range_of_scores == 0:
                normalized_score = 0.5
            else:
                normalized_score = max(
                    0.0,
                    min(1.0, (total_score - MIN_POSSIBLE_SCORE) / range_of_scores),
                )

            percentage = round(normalized_score * 100, 2)

            # 레이블 결정
            if percentage >= 75.0:
                label = "강한 긍정"
            elif percentage >= 53.0:
                label = "긍정"
            elif percentage <= 25.0:
                label = "강한 부정"
            elif percentage <= 47.0:
                label = "부정"
            else:
                label = "중립"

        return {
            "text": text,
            "tokens": tokens,
            "label": label,
            "score": total_score,
            "percentage": f"{percentage:.2f}%",
            "reason": details,
        }


class EmphaticSentimentAnalyzer:
    """
    외부에서 사용하는 감성 분석기 래퍼.
    - 내부적으로 MorphSentimentAnalyzer를 사용한다.
    - public 메서드는 analyze(text: str) 하나만 제공.
    """

    def __init__(self):
        self._impl = MorphSentimentAnalyzer()

    def analyze(self, text: str):
        return self._impl.text_analyze(text)


def analyze_txt_file(file_path: str):
    """
    지정된 TXT 파일을 읽고 줄별로 감성 분석을 수행하고,
    결과를 콘솔에 출력한다. (스크립트/디버그용)
    """
    analyzer = MorphSentimentAnalyzer()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print(f"[{file_path}] 파일이 비어 있습니다. 분석할 내용이 없습니다.")
            return

        print("=" * 70)
        print(f"파일명: {file_path}")
        print(f"총 {len(lines)}줄의 텍스트를 읽었습니다.")
        print("-" * 70)

        for idx, line in enumerate(lines, 1):
            text = line.strip()
            if not text:
                continue

            result = analyzer.text_analyze(text)

            print(f"[Line {idx} 분석 결과]")
            print(f"원문: {result['text']}")
            print(
                f"판정: {result['label']} (점수: {result['score']:+.2f}, "
                f"백분율: {result['percentage']})"
            )

            if result["reason"]:
                print("분석 과정:")
                for detail in result["reason"]:
                    print(f"    • {detail}")
            print("-" * 70)

    except FileNotFoundError:
        print(f"에러: 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요: '{file_path}'")
        print("팁: 이 Python 파일과 같은 폴더에 'input_data.txt' 파일을 넣어보세요.")
    except Exception as e:
        print(f"파일 처리 중 오류가 발생했습니다: {e}")
