#text 2
from konlpy.tag import Okt

class MorphSentimentAnalyzer:
    def __init__(self):
        self.okt = Okt() # 형태소 분석기 로드
        
        # 1. 감성 사전 (이제 '기본형'으로 작성해야 합니다)
        # 예: '예쁘' -> '예쁘다', '좋' -> '좋다'
        self.lexicon = {
            # 긍정
            "좋다": 1, "최고다": 2, "훌륭하다": 2, "추천하다": 1, "감동하다": 2,
            "행복하다": 2, "만족하다": 1, "예쁘다": 1, "빠르다": 1, "친절하다": 1,
            "성공하다": 1, "대박이다": 2, "귀엽다": 1, "아름답다": 1, 
            
            # 부정
            "싫다": -1, "나쁘다": -1, "최악이다": -2, "별로다": -1, "실망하다": -2,
            "느리다": -1, "비싸다": -1, "불친절하다": -2, "짜증나다": -1, 
            "아쉽다": -1, "어렵다": -1, "지저분하다": -1, "가관이다": -2
        }
        
        self.negators = ["안", "않다", "못", "없다", "아니다"]
        self.intensifiers = ["진짜", "정말", "매우", "완전", "너무", "엄청", "겁나", "가장"]

    def analyze(self, text):
        # [핵심] 문장을 형태소 단위로 쪼개고 '기본형'으로 바꿉니다 (stem=True)
        # 입력: "꽃이 참 예쁜 것 같아요" -> 출력: ['꽃', '이', '참', '예쁘다', '것', '같다']
        tokens = self.okt.morphs(text, stem=True)
        
        total_score = 0
        details = []

        # 토큰 리스트를 순회
        for i, token in enumerate(tokens):
            if token in self.lexicon:
                base_score = self.lexicon[token]
                current_score = base_score
                msg_parts = [f"'{token}'({base_score})"]

                # 문맥 검사 (현재 토큰의 앞 2개 단어 확인)
                # 리스트 인덱스로 접근하므로 더 정확함
                context_tokens = tokens[max(0, i-2):i] 

                # 1. 부정어 체크
                if any(neg in context_tokens for neg in self.negators):
                    current_score = -current_score
                    msg_parts.append(" + 부정어(반전)")
                
                # 2. 강조어 체크
                if any(inten in context_tokens for inten in self.intensifiers):
                    current_score *= 2
                    msg_parts.append(" + 강조어(x2)")

                total_score += current_score
                details.append(f"{''.join(msg_parts)}")

        # 결과 분류
        if total_score >= 3: label = "강한 긍정"
        elif total_score >= 1: label = "긍정"
        elif total_score <= -3: label = "강한 부정"
        elif total_score <= -1: label = "부정"
        else: label = "중립"

        return {
            "text": text,
            "tokens": tokens, # 변환된 토큰 확인용
            "label": label,
            "score": total_score,
            "reason": details
        }