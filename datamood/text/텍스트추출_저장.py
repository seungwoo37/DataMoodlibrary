import requests
from bs4 import BeautifulSoup
import os
import re

class Converter_save:

    #  User-Agent 헤더 정의 (봇 차단 우회) 
    # 대부분의 웹 서버는 이 헤더가 없으면 접근을 차단합니다.
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    @staticmethod
    def text_converter(url: str) -> tuple[str, str]:
        """
        주어진 URL에서 제목과 광고/잡텍스트를 제거한 본문 내용을 추출합니다.
        (네이버 블로그 iframe 및 User-Agent 처리 로직 포함)
        """
        soup = None
        
        # 1. 1차 웹 페이지 요청 및 BeautifulSoup 객체 생성
        try:
            # User-Agent 헤더를 사용하여 요청
            res = requests.get(url, headers=Converter_save.DEFAULT_HEADERS, timeout=10)
            res.raise_for_status() 
            res.encoding = 'utf-8'  
            soup = BeautifulSoup(res.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"URL 접근 또는 요청 중 오류 발생: {e}")
            return "오류: 페이지를 가져올 수 없음", ""

        
        
        # 제목 추출
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "제목을 찾을 수 없습니다"

        # 광고 및 불필요한 요소 사전 제거 (extract 사용)
        unwanted_patterns = [
            'ad', 'banner', 'share', 'sns', 'footer', 'copyright', 
            'related', 'aside', 'caption', 'byline', 'journalist'
        ]

        for pattern in unwanted_patterns:
            for tag in soup.find_all(lambda tag: tag.has_attr('class') and any(pattern in c.lower() for c in tag['class'])):
                tag.extract()
            for tag in soup.find_all(lambda tag: tag.has_attr('id') and pattern in tag['id'].lower()):
                tag.extract()
        
        for tag_name in ['script', 'style', 'img', 'iframe', 'button', 'a']:
            for tag in soup.find_all(tag_name):
                tag.extract()


        # 본문 추출 시도 (광고 제거 후)
        selectors = [
            {"class": "se-main-container"}, # 네이버 블로그 본문 최우선
            {"class": "se_doc_viewer"},     # 네이버 블로그 본문
            {"id": "article_content"},      # 일반 뉴스 기사
            {"class": "article_body"},
            {"class": "article_content"},
            {"name": "div", "attrs": {"id": lambda x: x and "article" in x.lower()}},
            {"name": "div", "attrs": {"class": lambda x: x and "article" in x.lower()}},
        ]

        article_text = None
        for sel in selectors:
            if 'name' in sel:
                article_div = soup.find(sel['name'], **sel['attrs'])
            else:
                article_div = soup.find("div", **sel)

            if article_div:
                article_text = article_div.get_text("\n", strip=True)
                break

        # 본문 정리 (Fallback 및 필터링)
        if not article_text:
            article_text = soup.get_text("\n")

        result_lines = []
        cleaned_text = re.sub(r'\n+', '\n', article_text).strip()
        lines = cleaned_text.split("\n")

        # 필터링 조건: 길이 완화 및 저작권 키워드 제거
        forbidden_patterns = ["저작권", "ⓒ", "@", "무단전재", "배포금지"]

        for line in lines:
            line = line.strip()
            
            # 길이 검사 완화: 5자 이상
            if len(line) > 5 and not any(pattern in line for pattern in forbidden_patterns):
                # 단어당 글자 수가 너무 적은 (기호나 공백만 많은) 줄 방지
                if len(line.split()) == 0 or len(line) / len(line.split()) > 3:
                    result_lines.append(line)

        # 최종 텍스트 정리
        article = "\n".join(result_lines)

        return title, article

    @staticmethod
    def save_to_file(title: str, body: str, directory: str = ".", filename_prefix: str = "article") -> str | None:
        safe_title = "".join(c if c.isalnum() or c.isspace() else '_' for c in title)
        safe_title = safe_title[:50].strip()
        
        filename = f"{filename_prefix}_{safe_title}.txt"
        
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"제목: {title}\n\n")
                f.write("----------------------------------------\n\n")
                f.write(body)

            print(f"파일 저장 성공: {filepath}")
            return filepath

        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")
            return None