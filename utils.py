import os
import openai
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import streamlit as st


load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

openai.api_key = st.secrets["OPENAI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# st.secrets 추출 정보 확인

def get_st_secrets_brief():
    brief_str = ""
    if openai.api_key:
        brief_str += openai.api_key[-5:]
    if GOOGLE_API_KEY:
        brief_str += " "
        brief_str += GOOGLE_API_KEY[-5:]
    if GOOGLE_CSE_ID:
        brief_str += " "
        brief_str += GOOGLE_CSE_ID[-5:]
    return brief_str

# GPT를 통해 Google 검색용 질의 생성
def generate_google_query(user_input):
    prompt = f"""
    아래 질문 내용을 바탕으로 뉴스 기반 ETF 종목 탐색에 적합한 구글 검색에 유리한 형태의 명료한 검색 질의어로 변경해줘.
    구글 검색의 특성에 맞게 구체적인 키워드 단위로 추출되는게 필요하고, 전체 문장을 따옴표로 감싸게 되면 문장 전체가 일치하는 검색결과만 나오게 되니 절대 감싸지 말아줘:

    질문: {user_input}
    검색 질의어:
    """
    response = openai.ChatCompletion.create(
        # model="gpt-4o-mini-2024-07-18",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0,
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
    response = requests.get(search_url, params=params)
    response_json = response.json()

    links = [item['link'] for item in response_json.get('items', [])]
    return links, response

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
    <질문>
    {question}
    </질문>

    다음은 구글 검색을 통해 얻은 관련 정보이다:
    <정보>
    {scraped_text}
    </정보>

    위 정보를 기반으로 고객 질문에 600자 이내의 간결한 답변을 해줘.
    또한 답변과 관련하여 고객이 명시한 ETF 개수가 있으면 정확히 그 수만큼, 없으면 질문 성격상 최소 1개에서 최대 {etf_count}개의 한국 상장 ETF 종목과 티커명을 함께 추천해줘.
    
    반드시 다음 형식을 준수해 응답해. 다음 형식을 준수해서 응답하지 않으면 이후 진행이 이루어지지 않으니 답변 형식은 필수적으로 준수해야해.
    
    답변: (간략한 답변 내용)
    ETF추천:
    1. 종목명 [[티커]]
    2. 종목명 [[티커]]
    (종목수는 요청에 맞게)

    답변:
    """
    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0,
    )
    return response.choices[0].message['content'].strip()

# GPT 응답 파싱
def parse_gpt_response(response_text):
    lines = response_text.split("\n")
    answer = lines[0].replace("답변:", "").strip()
    etfs = []
    for line in lines[2:]:
        print(f"line: {line}")
        if line.strip():
            try:
                etf_info = line.split('. ')[1]
                name, ticker = etf_info.rsplit('[[', 1)
                ticker = ticker.replace(']]', '').strip()
                name = name.strip()
                etfs.append((name, ticker))
            except:
                print(f"exception: {line}")

    return answer, etfs
