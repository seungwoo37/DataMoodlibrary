#최종_완성_테스트
# datamood/text/text_mood.py
from konlpy.tag import Okt
import math
from 텍스트추출_저장 import Converter_save

class MorphSentimentAnalyzer:
    """
    형태소 분석(Okt) + 간단한 lexicon + 부정어/강조어/TF-IDF 개념을 이용한 감성 분석기.
    """

    def __init__(self):
        self.okt = Okt()
        
        # 확장된 감성 사전
        self.lexicon = {
            # 강한 긍정 (+2)
            "최고다": 2, "훌륭하다": 2, "행복하다": 2, "대박이다": 2, "재미있다": 2,
            "완벽하다": 2, "멋지다": 2, "환상적이다": 2, "놀랍다": 2, "탁월하다": 2,
            "감격하다": 2, "황홀하다": 2, "대박": 2, "최고": 2, "끝내주다": 2,
            "만족스럽다": 2, "훌륭": 2, "완벽": 2, "멋": 2, 
            
            # 긍정 (+1)
            "좋다": 1, "추천하다": 1, "감동하다": 1, "만족하다": 1, "예쁘다": 1,
            "빠르다": 1, "친절하다": 1, "성공하다": 1, "귀엽다": 1, "아름답다": 1,
            "감사하다": 1, "고맙다": 1, "뛰어나다": 1, "괜찮다": 1,
            "감동": 1, "유익하다": 1, "신선하다": 1, "산뜻하다": 1,
            "추천": 1, "만족": 1, "좋": 1, "훌륭": 1, "감사": 1, "고마움": 1,
            "매력적이다": 1, "매력": 1, "흥미롭다": 1, "유쾌하다": 1, "즐겁다": 1,
            "편하다": 1, "편안하다": 1, "쾌적하다": 1, "상쾌하다": 1, "든든하다": 1,
            "유용하다": 1, "효과적이다": 1, "효율적이다": 1, "탁월": 1,
            "사랑스럽다": 1, "매혹적이다": 1, "인상적이다": 1, "멋있다": 1,
            "보람있다": 1, "화려하다":1, 
            
            # 강한 부정 (-2)
            "최악이다": -2, "실망하다": -2, "불친절하다": -2, "끔찍하다": -2,
            "혐오스럽다": -2, "역겹다": -2, "지루하다": -2, "화나다": -2,
            "격노하다": -2, "고통스럽다": -2, "처참하다": -2, "최악": -2,
            "형편없다": -2, "엉망이다": -2, "실패하다": -2,
            
            # 부정 (-1)
            "싫다": -1, "나쁘다": -1, "별로다": -1, "느리다": -1, "비싸다": -1,
            "짜증나다": -1, "아쉽다": -1, "어렵다": -1, "지저분하다": -1,
            "불편하다": -1, "답답하다": -1, "걱정하다": -1, "미안하다": -1,
            "슬프다": -1, "구리다": -1, "별로": -1, "불만스럽다": -1,
            "실망": -1, "후회하다": -1, "안타깝다": -1, "아쉬움": -1,
            "불만": -1, "짜증": -1, "불쾌하다": -1, "불만족스럽다": -1,
            "불안하다": -1, "우울하다": -1, "피곤하다": -1, "힘들다": -1,
            "복잡하다": -1, "애매하다": -1, "모호하다": -1, "의심스럽다": -1,
            "불안":-1, "불안감을":-1, 
        }
        
        # 어간 매핑 사전 추가 (Okt가 놓칠 수 있는 변형들)
        self.stem_mapping = {
            "만족스럽": "만족스럽다",
            "훌륭": "훌륭하다",
            "완벽": "완벽하다",
            "멋지": "멋지다",
            "추천": "추천하다",
            "만족": "만족하다",
            "감동": "감동하다",
            "실망": "실망하다",
            "후회": "후회하다",
            "좋": "좋다",
            "나쁘": "나쁘다",
            "싫": "싫다",
            "재미있": "재미있다",
            "지루": "지루하다",
            "매력적": "매력적이다",
            "매력": "매력적이다",
            "흥미롭": "흥미롭다",
            "유쾌": "유쾌하다",
            "즐겁": "즐겁다",
            "편": "편하다",
            "편안": "편안하다",
            "불편": "불편하다",
            "불쾌": "불쾌하다",
            "인상적": "인상적이다",
            "효과적": "효과적이다",
            "효율적": "효율적이다",
        }
        
        # 동적 IDF 가중치 계산을 위한 문서 빈도 (가상의 코퍼스 기반)
        self.idf_weights = {
            # 강한 감성어 - 높은 가중치
            "최고다": 2.5, "최악이다": 2.5, "대박이다": 2.3, "재미있다": 2.0,
            "끔찍하다": 2.3, "완벽하다": 2.2, "실망하다": 2.0, "감격하다": 2.2,
            "대박": 2.3, "최고": 2.5, "최악": 2.5,
            
            # 중간 강도 감성어
            "좋다": 1.5, "나쁘다": 1.5, "감동하다": 1.7, "비싸다": 1.6,
            "불친절하다": 1.8, "만족하다": 1.6, "감동": 1.7, "매력적이다": 1.4,
            
            # 일반 감성어
            "싫다": 1.3, "빠르다": 1.2, "느리다": 1.2, "예쁘다": 1.3,
            "별로": 1.4, "아쉽다": 1.3, "괜찮다": 1.2,
            
            # 중립/일반 단어
            "영화": 0.8, "서비스": 0.8, "가격": 0.8, "품질": 0.8,
            "것": 0.5, "같다": 0.5, "이": 0.3, "그": 0.3,
        }
        
        # 부정어 (더 확장)
        self.negators = ["안", "않다", "못", "없다", "아니다", "말다", "아니"]
        
        # 강조어 (레벨별 분류)
        self.strong_intensifiers = ["완전", "진짜", "정말", "엄청", "너무", "매우", "굉장히", "아주"]
        self.mild_intensifiers = ["꽤", "제법", "좀", "약간", "다소"]
        
        # 약화어 추가
        self.weakeners = ["조금", "살짝", "약간", "다소", "그나마", "그런대로"]
        
        # 품사 태그
        self.target_pos = ['Noun', 'Verb', 'Adjective', 'Adverb']
        
        # 부정어 반전 제외 단어 (자체적으로 부정 의미)
        self.no_negation_flip = [
            "별로", "최악", "최악이다", "싫다", "나쁘다", "끔찍하다",
            "형편없다", "엉망이다", "구리다"
        ]
        
        # 접속사 및 전환 표현 (감성 전환 감지용)
        self.conjunctions = ["하지만", "그러나", "그런데", "근데", "but", "BUT"]

    def calculate_sentence_length_factor(self, num_tokens):
        """문장 길이에 따른 보정 계수"""
        if num_tokens < 5:
            return 1.2  # 짧은 문장은 각 단어의 영향력 증가
        elif num_tokens > 20:
            return 0.9  # 긴 문장은 영향력 분산
        return 1.0

    def detect_sentiment_transition(self, tokens):
        """접속사를 기준으로 감성 전환 감지"""
        transitions = []
        for i, token in enumerate(tokens):
            if token in self.conjunctions:
                transitions.append(i)
        return transitions

    def get_sentiment_score(self, token):
        """토큰의 감성 점수를 반환 (어간 매핑 포함)"""
        # 직접 매칭
        if token in self.lexicon:
            return self.lexicon[token]
        
        # 어간 매핑 시도
        if token in self.stem_mapping:
            mapped_token = self.stem_mapping[token]
            if mapped_token in self.lexicon:
                return self.lexicon[mapped_token]
        
        # 부분 매칭 시도 (어간이 포함된 경우)
        for stem, full_word in self.stem_mapping.items():
            if token.startswith(stem) and full_word in self.lexicon:
                return self.lexicon[full_word]
            if stem == token and full_word in self.lexicon:
                return self.lexicon[full_word]
                
        return None



    def text_analyze(self, text):
        # 형태소 분석
        raw_tokens_pos = self.okt.pos(text, stem=True)
        
        # 토큰 필터링 및 TF 계산
        tokens = []
        tf_count = {}
        pos_tags = {}
        
        for token, pos in raw_tokens_pos:
            if pos in self.target_pos or token in self.lexicon or self.get_sentiment_score(token) is not None:
                tokens.append(token)
                tf_count[token] = tf_count.get(token, 0) + 1
                pos_tags[token] = pos
        
        # 감성 전환 지점 탐지
        transitions = self.detect_sentiment_transition(tokens)
        
        # 문장 길이 보정 계수
        length_factor = self.calculate_sentence_length_factor(len(tokens))
        
        total_score = 0
        details = []
        sentiment_words = [token for token in tokens if self.get_sentiment_score(token) is not None]
        num_sentiment_words = len(sentiment_words)
        
        # 정규화를 위한 최대/최소 점수 계산
        MAX_POSSIBLE_SCORE = num_sentiment_words * 5  # 최대: 기본2 * IDF2.5 * 강조2
        MIN_POSSIBLE_SCORE = num_sentiment_words * -5
        
        if num_sentiment_words == 0:
            percentage = 50.0
            label = "중립"
        else:
            for i, token in enumerate(tokens):
                base_score = self.get_sentiment_score(token)
                if base_score is not None:
                    current_score = base_score
                    
                    # TF-IDF 가중치
                    idf_weight = self.idf_weights.get(token, 1.0)
                    tf = tf_count[token]
                    
                    # 로그 스케일 TF 적용 (과도한 반복 방지)
                    tf_scaled = 1 + math.log(tf) if tf > 1 else tf
                    
                    current_score *= tf_scaled * idf_weight
                    
                    msg_parts = [f"'{token}'({base_score}*TF{tf_scaled:.2f}*IDF{idf_weight:.1f})"]
                    
                    # 문맥 분석 (앞뒤 3개 토큰)
                    context_before = tokens[max(0, i-3):i]
                    context_after = tokens[i+1:min(len(tokens), i+4)]
                    context_tokens = context_before + context_after
                    
                    # 부정어 처리
                    if any(neg in context_tokens for neg in self.negators) and token not in self.no_negation_flip:
                        current_score = -current_score
                        msg_parts.append("부정어(반전)")
                    
                    # 강조어 처리 (레벨별)
                    if any(inten in context_tokens for inten in self.strong_intensifiers):
                        current_score *= 2.0
                        msg_parts.append("강한강조(x2.0)")
                    elif any(inten in context_tokens for inten in self.mild_intensifiers):
                        current_score *= 1.5
                        msg_parts.append("약한강조(x1.5)")
                    
                    # 약화어 처리
                    if any(weak in context_tokens for weak in self.weakeners):
                        current_score *= 0.7
                        msg_parts.append("약화어(x0.7)")
                    
                    # 감성 전환 후 위치면 가중치 증가
                    in_transition_zone = any(i > trans for trans in transitions)
                    if in_transition_zone and transitions:
                        current_score *= 1.3
                        msg_parts.append("전환후(x1.3)")
                    
                    # 문장 길이 보정
                    current_score *= length_factor
                    
                    total_score += current_score
                    details.append(f"{' + '.join(msg_parts)} → {current_score:+.2f}")
            
            # 정규화
            range_of_scores = MAX_POSSIBLE_SCORE - MIN_POSSIBLE_SCORE
            
            if range_of_scores == 0:
                normalized_score = 0.5
            else:
                normalized_score = max(0.0, min(1.0, (total_score - MIN_POSSIBLE_SCORE) / range_of_scores))
            
            percentage = normalized_score * 100
            
            
            # 세분화된 라벨링
            if percentage >= 80.0:
                label = "매우 긍정적"
            elif percentage >= 60.0:
                label = "긍정적"
            elif percentage >= 52.0:
                label = "약간 긍정적"
            elif percentage <= 20.0:
                label = "매우 부정적"
            elif percentage <= 40.0:
                label = "부정적"
            elif percentage <= 48.0:
                label = "약간 부정적"
            else:
                label = "중립적"
        
        rst = {
            "text": text,
            "tokens": tokens,
            "label": label,
            "score": round(total_score, 2),
            "percentage": round(percentage, 2),
            "num_sentiment_words": num_sentiment_words,
            "total_words": len(tokens),
            "reason": details
        }
        
        print(f"원문: {rst['text']}")
        print(
            f"판정: {rst['label']} (점수: {rst['score']:+.2f}, "
            f"백분율: {rst['percentage']})"
            )

        if rst["reason"]:
            print("분석 과정:")
            for detail in rst["reason"]:
                print(f"    • {detail}")
        print("-" * 70)

        return {
            "text": text,
            "tokens": tokens,
            "label": label,
            "score": round(total_score, 2),
            "percentage": round(percentage, 2),
            "num_sentiment_words": num_sentiment_words,
            "total_words": len(tokens),
            "reason": details
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
    
    def analyze_txt_file(self, file_path: str):
        """
        지정된 TXT 파일을 읽고 줄별로 감성 분석을 수행하고,
        결과를 콘솔에 출력한다.
        """

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

                result = self._impl.text_analyze(text)

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
            
    def analyze_url(self, url: str):
        """
        기사/블로그 등의 URL을 받아서
        - Converter_save로 제목, 본문을 추출하고
        - 본문 텍스트에 대해 감정 분석을 수행한다.
        """
        # 1) URL에서 제목, 본문 추출
        title, body = Converter_save.text_converter(url)

        # 2) 본문이 비어 있으면 기본값 반환
        if not body.strip():
            return {
                "text": body,
                "tokens": [],
                "label": "중립",
                "score": 0.0,
                "percentage": 50.0,
                "num_sentiment_words": 0,
                "total_words": 0,
                "reason": [],
                "title": title,
                "url": url,
                "source": "url",
            }

        # 3) 기존 analyze() 재사용해서 감정 분석
        base_result = self.analyze(body)  # dict 구조 그대로 들어옴

        # 4) 메타 정보(제목, URL, source)만 덧붙여서 반환
        base_result["title"] = title
        base_result["url"] = url
        base_result["source"] = "url"

        return base_result
    

if __name__ == "__main__":
    print("=" * 80)
    print("한국어 형태소 기반 감성 분석 시스템 (TF-IDF 결합)")
    print("=" * 80)
    print()

    analyzer = MorphSentimentAnalyzer()

    # TF-IDF 가중치 적용으로 인해, 이제 단순히 +1, -1 점이 아닌 소수점 점수가 나올 수 있습니다.
    test_sentences = [
        "이 영화 정말 너무 재미있었어요!",         # 재미있다(2.0 * 1.8) * 강조(x2) = +7.2
        "서비스가 별로 좋지 않았습니다.",           # 좋다(1.0 * 1.5) * 반전 = -1.5
        "가격은 비싸지만 품질이 훌륭해요.",          # 비싸다(-1.0 * 1.5) + 훌륭하다(2.0 * 1.7) = -1.5 + 3.4 = +1.9 -> +1.71 (부정어 약화)
        "완전 최악이에요... 다시는 안 올 거예요.", # 최악(-2.0 * 2.0) * 강조(x2) = -8.0
        "그냥 평범한 것 같아요.",
        "진짜 감동적이었고 배우들 연기도 대박이었어요!" # 감동(1.0*1.5)*강조(x2) + 대박(2.0*1.8) = +3.0 + 3.6 = +6.6
        ]
        
    for idx, sentence in enumerate(test_sentences, 1):
        print(f"\n[테스트 {idx}/{len(test_sentences)}]")
        result = analyzer.text_analyze(sentence)
                
        if "error" in result:
            print(f"에러: {result['error']}")
            continue
                
        print(f"원문: {result['text']}")
        print(f"토큰: {' / '.join(result['tokens'])}")
        print(f"판정: {result['label']} (점수: {result['score']:+.2f}, 백분율: {result['percentage']})")
        if result['reason']:
            print(f"분석 과정:")
            for detail in result['reason']:
                print(f"   • {detail}")
        print("-" * 80)
        
    print("\n분석 완료!")
    print("=" * 80)