import os
import openai
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# GPT를 통해 Google 검색용 질의 생성
def generate_google_query(user_input):
    prompt = f"""
    아래 질문을 구글 검색에 유리한 형태의 명료한 검색 질의어로 변경해줘:
    질문: {user_input}
    검색 질의어:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0.2,
    )
    query = response.choices[0].message['content'].strip()
    return query

# Google 검색 수행 후 상위 3개 URL 반환
def google_search(query, num_results=3):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results
    }
    response = requests.get(search_url, params=params).json()
    links = [item['link'] for item in response.get('items', [])]
    return links

# 웹페이지 내용 추출
def scrape_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    texts = soup.stripped_strings
    return " ".join(texts)[:3000]  # GPT 최대 토큰 제한 고려

# GPT API로 투자 질문에 대한 응답 생성
def generate_gpt_response(question, scraped_text, etf_count=3):
    prompt = f"""
    다음은 고객의 투자 질문이다:
    "{question}"

    다음은 구글 검색을 통해 얻은 관련 정보이다:
    "{scraped_text}"

    위 정보를 기반으로 고객 질문에 300자 이내의 간결한 답변을 해줘.
    또한 답변과 관련하여 고객이 명시한 ETF 개수가 있으면 정확히 그 수만큼, 없으면 질문 성격상 최소 1개에서 최대 3개의 한국 상장 ETF 종목과 티커명을 함께 추천해줘.
    
    반드시 다음 형식을 준수해 응답해:
    
    답변: (간략한 답변 내용)
    ETF추천:
    1. 종목명 (티커)
    2. 종목명 (티커)
    (종목수는 요청에 맞게)

    답변:
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.5,
    )
    return response.choices[0].message['content'].strip()

# GPT 응답 파싱
def parse_gpt_response(response_text):
    lines = response_text.split("\n")
    answer = lines[0].replace("답변:", "").strip()
    etfs = []
    for line in lines[2:]:
        if line.strip():
            etf_info = line.split('. ')[1]
            name, ticker = etf_info.rsplit('(', 1)
            ticker = ticker.replace(')', '').strip()
            name = name.strip()
            etfs.append((name, ticker))
    return answer, etfs
