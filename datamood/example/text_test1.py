# 백분율 추가 테스트
from konlpy.tag import Okt

class MorphSentimentAnalyzer:
    def __init__(self):
        self.okt = Okt() # 형태소 분석기 로드
        
        # 1. 감성 사전 (기본형)
        self.lexicon = {
            # 긍정 (최대 +2)
            "좋다": 1, "최고다": 2, "훌륭하다": 2, "추천하다": 1, "감동하다": 2,
            "행복하다": 2, "만족하다": 1, "예쁘다": 1, "빠르다": 1, "친절하다": 1,
            "성공하다": 1, "대박이다": 2, "귀엽다": 1, "아름답다": 1, "가뿐하다": 1, 
            "감개무량하다":1, "감격하다":1, "감동하다":1, "감미롭다":1, "감복하다":1,
            "감사하다":1, "경이롭다":1, "경쾌하다":1, "고맙다":1, "재미있다":1,
            "대박":1, "최고":2, "감동":1, "성공":1, "친절":1,
            

            # 부정 (최소 -2)
            "싫다": -1, "나쁘다": -1, "최악이다": -2, "별로다": -1, "실망하다": -2,
            "느리다": -1, "비싸다": -1, "불친절하다": -2, "짜증나다": -1, 
            "아쉽다": -1, "어렵다": -1, "지저분하다": -1, "가관이다": -2,
            "가련하다": -1,"가소롭다": -1, "가슴아프다": -2, "가엾다": -1,
            "각박하다":-1, "간절하다": -1, "갑갑하다": -1, "거북하다":-1,
            "걱정하다":-1, "겁나다":-1, "격노하다":-2, "격분하다":-2,
            "격양되다":-1, "격해지다":-1, "경박하다":-2, "경악하다":-2,
            "고달프다":-1, "고독하다":-2, "고리타분하다":-1, "고통스럽다":-1,
            "공허하다":-1, "괘씸하다":-1, "괴상하다":-1, "구역질나다":-1,
            "최악":-1, "경악":-2
        }
        
        self.negators = ["안", "않다", "못", "없다", "아니다"]
        # 강조어는 점수를 2배로 만듦
        self.intensifiers = ["진짜", "정말", "매우", "완전", "너무", "엄청", "겁나", "가장"]

    def analyze(self, text):
        tokens = self.okt.morphs(text, stem=True)
        
        total_score = 0
        details = []

        # 백분율 계산을 위한 점수 범위 설정
        
        # 1. 문장에서 감성 단어 목록 추출 및 최대/최소 감성 점수 계산
        sentiment_words = [token for token in tokens if token in self.lexicon]
        num_sentiment_words = len(sentiment_words)
        
        # 문장 내에서 이론적으로 가능한 최대 긍정 점수와 최소 부정 점수를 설정합니다.
        # (최대 점수 2 * 강조어 2배 = 4)
        MAX_POSSIBLE_SCORE = num_sentiment_words * 4
        MIN_POSSIBLE_SCORE = num_sentiment_words * -4
        
        # 감성 단어가 없으면 중립으로 처리
        if num_sentiment_words == 0:
            percentage = 50.0
            label = "중립"
        else:
            # 토큰 리스트를 순회하며 total_score 계산
            for i, token in enumerate(tokens):
                if token in self.lexicon:
                    base_score = self.lexicon[token]
                    current_score = base_score
                    msg_parts = [f"'{token}'({base_score})"]

                    # === [수정된 부분] ===
                    # 부정어/강조어 체크를 위해 앞 2개, 뒤 2개의 토큰을 확인합니다.
                    # 예: '좋' + '지 않다' 구조에서 '않다'가 '좋다' 뒤에 있어도 탐지 가능
                    context_before = tokens[max(0, i-2):i]
                    context_after = tokens[i+1:min(len(tokens), i+3)]
                    context_tokens = context_before + context_after
                    
                    # 1. 부정어 체크
                    if any(neg in context_tokens for neg in self.negators):
                        current_score = -current_score
                        msg_parts.append(" + 부정어(반전)")
                    
                    # 2. 강조어 체크
                    if any(inten in context_tokens for inten in self.intensifiers):
                        current_score *= 2
                        msg_parts.append(" + 강조어(x2)")

                    total_score += current_score
                    details.append(f"{''.join(msg_parts)} (최종: {current_score:+.1f})")
                    if any(neg in tokens for neg in self.negators):
                        if total_score>0:
                            total_score *= 0.9
                            details.append(">> 전체 부정어 감지: 긍정 점수 ")

            # 2. 백분율 정규화 (Min-Max Normalization과 유사)
            range_of_scores = MAX_POSSIBLE_SCORE - MIN_POSSIBLE_SCORE
            
            # ZeroDivisionError 방지
            if range_of_scores == 0:
                normalized_score = 0.5 # 점수가 모두 0인 경우
            else:
                normalized_score = (total_score - MIN_POSSIBLE_SCORE) / range_of_scores
            
            # 0% ~ 100%로 변환
            percentage = round(normalized_score * 100, 2)

            # 3. 백분율 기반 결과 분류 (50%를 중립 기준으로 사용)
            if percentage >= 75.0:
                label = "강한 긍정"
            elif percentage >= 55.0:
                label = "긍정"
            elif percentage <= 25.0:
                label = "강한 부정"
            elif percentage <= 45.0:
                label = "부정"
            else:
                label = "중립"
        
        return {
            "text": text,
            "tokens": tokens, 
            "label": label,
            "score": total_score,
            "percentage": f"{percentage:.2f}%", # 백분율 결과 추가
            "reason": details
        }
if __name__ == "__main__":
    print("=" * 80)
    print("한국어 형태소 기반 감성 분석 시스템")
    print("=" * 80)
    print()

    analyzer = MorphSentimentAnalyzer()

    test_sentences = [
        "이 영화 정말 너무 재미있었어요!",
        "서비스가 별로 좋지 않았습니다.", # <--- 이 문장의 분석 결과가 '부정'으로 바뀔 가능성이 높음
        "가격은 비싸지만 품질이 훌륭해요.",
        "완전 최악이에요... 다시는 안 올 거예요.",
        "그냥 평범한 것 같아요.",
        "진짜 감동적이었고 배우들 연기도 대박이었어요!"
        ]
        
    for idx, sentence in enumerate(test_sentences, 1):
        print(f"\n[테스트 {idx}/{len(test_sentences)}]")
        result = analyzer.analyze(sentence)
                
        if "error" in result:
            print(f"에러: {result['error']}")
            continue
                
        print(f"원문: {result['text']}")
        print(f"토큰: {' / '.join(result['tokens'])}")
        if result['reason']:
            print(f"분석 과정:")
            for detail in result['reason']:
                print(f"   • {detail}")
        print(f"판정: {result['label']} (점수: {result['score']:+.1f}, 백분율: {result['percentage']})")
        print("-" * 80)
        
    print("\n분석 완료!")
    print("=" * 80)