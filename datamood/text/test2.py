#TF-IDF개념 적용 테스트
from konlpy.tag import Okt

class MorphSentimentAnalyzer:
    def __init__(self):
        self.okt = Okt() # 형태소 분석기 로드
        
        # 1. 감성 사전 (Lexicon) - 이전 논의 반영
        self.lexicon = {
            # 긍정 (최대 +2)
            "좋다": 1, "최고다": 2, "훌륭하다": 2, "추천하다": 1, "감동하다": 1, 
            "행복하다": 2, "만족하다": 1, "예쁘다": 1, "빠르다": 1, "친절하다": 1,
            "성공하다": 1, "대박이다": 2, "귀엽다": 1, "아름답다": 1, "가뿐하다": 1, 
            "감개무량하다":1, "감격하다":1, "감미롭다":1, "감복하다":1, "감사하다":1,
            "경이롭다":1, "경쾌하다":1, "고맙다":1, 
            "재미있다": 2, "감동": 1, "대박": 2, 

            # 부정 (최소 -2)
            "싫다": -1, "나쁘다": -1, "최악이다": -2, "별로다": -1, "실망하다": -2,
            "느리다": -1, "비싸다": -1, "불친절하다": -2, "짜증나다": -1, 
            "아쉽다": -1, "어렵다": -1, "지저분하다": -1, "가관이다": -2,
            "가련하다": -1,"가소롭다": -1, "가슴아프다": -2, "가엾다": -1,
            "각박하다":-1, "간절하다": -1, "갑갑하다": -1, "거북하다":-1,
            "걱정하다":-1, "겁나다":-1, "격노하다":-2, "격분하다":-2,
            "고달프다":-1, "고독하다":-2, "고통스럽다":-1, "최악": -2, "별로": -1,
            "미안하다":-1, "슬프다":-1, "처참하다": -2, "구리다":-1
        }
        
        # 2. TF-IDF 가중치 (IDF 가상 설정) 
        # 자주 쓰이는 감성 단어일수록 가중치를 높게 설정 (TF-IDF는 희귀도에 비례)
        self.idf_weights = {
            # 높은 가중치 (감성 핵심어, 희귀어처럼 취급)
            "최고다": 2.0, "최악이다": 2.0, "대박이다": 1.8, "재미있다": 1.8, "훌륭하다": 1.7, "실망하다": 1.7,
            "좋다": 1.5, "나쁘다": 1.5, "감동하다": 1.5, "비싸다": 1.5, "불친절하다": 1.5, "짜증나다": 1.5,
            "감동": 1.5, "대박": 1.8, "최악": 2.0,
            
            # 일반/중간 가중치 (일반적인 감성어)
            "싫다": 1.0, "만족하다": 1.0, "빠르다": 1.0, "느리다": 1.0,
            
            # 낮은 가중치 (자주 쓰이는 중립 부사/기능어처럼 취급. 이 단어들은 lexicon에 없더라도 IDF는 설정 가능)
            "영화": 0.8, "서비스": 0.8, "가격": 0.8, "품질": 0.8, "연기": 0.8, "상태": 0.8 ,"것": 0.5, "같다": 0.5
        }
        
        self.negators = ["안", "않다", "못", "없다", "아니다"]
        self.intensifiers = ["진짜", "정말", "매우", "완전", "너무", "엄청", "겁나", "가장", "참"] 

    def analyze(self, text):
        # TF 계산을 위해, 토큰화 후 빈도수를 먼저 계산
        tokens = self.okt.morphs(text, stem=True)
        tf_count = {}
        for token in tokens:
            tf_count[token] = tf_count.get(token, 0) + 1
        
        total_score = 0
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
                    current_score = base_score
                    
                    # 1. TF-IDF 가중치 적용 (Lexicon Score * TF-IDF Weight)
                    # TF-IDF 가중치가 없으면 기본 1.0 적용
                    idf_weight = self.idf_weights.get(token, 1.0)
                    tf = tf_count[token]
                    # 최종 가중치는 TF * IDF (여기서는 TF * IDF_Weight)
                    weighted_score_multiplier = tf * idf_weight
                    
                    # 기본 점수에 TF-IDF 가중치를 곱함
                    current_score *= weighted_score_multiplier 
                    
                    msg_parts = [f"'{token}'({base_score}*TF{tf}*IDF{idf_weight:.1f})"]

                    # 앞 2개, 뒤 2개 토큰을 확인.
                    context_before = tokens[max(0, i-2):i]
                    context_after = tokens[i+1:min(len(tokens), i+3)]
                    context_tokens = context_before + context_after
                    
                    # 2. 부정어 체크 (부호 반전)
                    if any(neg in context_tokens for neg in self.negators):
                        current_score = -current_score
                        msg_parts.append(" + 부정어(반전)")
                    
                    # 3. 강조어 체크 (x2)
                    if any(inten in context_tokens for inten in self.intensifiers):
                        current_score *= 2
                        msg_parts.append(" + 강조어(x2)")

                    total_score += current_score
                    details.append(f"{''.join(msg_parts)} (최종: {current_score:+.2f})")

            # 4. 문장 내 전체 부정어 체크 및 최종 점수 조정 
            if any(neg in tokens for neg in self.negators):
                if total_score > 0:
                    total_score *= 0.9  
                    details.append(">> 전체 부정어 감지: 긍정 점수 0.9배 약화")
            
            # 5. 백분율 정규화 (최대/최소 점수는 여전히 4점 기준으로 계산)
            range_of_scores = MAX_POSSIBLE_SCORE - MIN_POSSIBLE_SCORE
            
            if range_of_scores == 0:
                normalized_score = 0.5 
            else:
                # TF-IDF가 적용되어 total_score가 MAX_POSSIBLE_SCORE를 초과할 수 있음.
                # 백분율을 0~100% 범위로 제한
                normalized_score = max(0.0, min(1.0, (total_score - MIN_POSSIBLE_SCORE) / range_of_scores))
            
            percentage = round(normalized_score * 100, 2)

            # 6. 백분율 기반 결과 분류 
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
            "reason": details
        }
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
        result = analyzer.analyze(sentence)
                
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