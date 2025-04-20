import streamlit as st
from utils import (
    generate_google_query, google_search, scrape_text_from_url, generate_gpt_response, parse_gpt_response
)

st.title("📈 간단 투자상담 챗봇 (GPT + Google)")

user_question = st.text_input("💬 투자 관련 질문을 입력하세요:",
    placeholder="예) 관세전쟁 시대에 투자에 유리한 한국 ETF 3개 찾아줘")

if st.button("상담 받기") and user_question:
    with st.spinner("🔍 검색 및 분석 중입니다..."):
        # 구글 질의어 생성
        search_query = generate_google_query(user_question)
        
        # 구글 검색 실행 및 텍스트 수집
        urls = google_search(search_query)
        combined_text = ""
        for url in urls:
            combined_text += scrape_text_from_url(url) + " "

        # ETF 개수 파악
        import re
        match = re.search(r'(\d+)개', user_question)
        etf_count = int(match.group(1)) if match else 3

        # GPT 응답 생성 및 파싱
        gpt_response = generate_gpt_response(user_question, combined_text, etf_count)
        answer, etf_list = parse_gpt_response(gpt_response)

    # 결과 표시
    st.subheader("🔖 상담 답변")
    st.info(answer)

    st.subheader("📌 추천 ETF")
    for name, ticker in etf_list:
        # link = f"https://finance.naver.com/search/searchList.naver?query={ticker}"
        link = f"https://finance.naver.com/item/main.naver?code={ticker}"
        
        st.markdown(f"- [{name} ({ticker})]({link})", unsafe_allow_html=True)
