import streamlit as st
from utils import (
    get_st_secrets_brief, generate_google_query, google_search, scrape_text_from_url, generate_gpt_response, parse_gpt_response
)

st.title("📈 GPT로 직접 답변하는 키우Me 컨셉")

# st.write(f"st.secrets: {get_st_secrets_brief()}")

user_question = st.text_input("💬 투자 관련 질문을 입력하세요:",
    # value="관세전쟁에 유리한 한국 ETF 3개 찾아줘",
    placeholder="예) 관세전쟁에 유리한 한국 ETF 3개 찾아줘")

# if st.button("상담 받기") and user_question:
if user_question:
    with st.spinner("🔍 검색 및 분석 중입니다..."):
        # 구글 질의어 생성
        search_query = generate_google_query(user_question)
        
        # 구글 검색 실행 및 텍스트 수집
        urls, response = google_search(search_query)
        status_code = response.status_code

        combined_text = ""
        for url in urls:
            combined_text += scrape_text_from_url(url) + " "

        # ETF 개수 파악
        import re
        match = re.search(r'(\d+)(개|종류|종|가지)', user_question)
        etf_count = int(match.group(1)) if match else 3

        # GPT 응답 생성 및 파싱
        gpt_response = generate_gpt_response(user_question, combined_text, etf_count)
        print(f"gpt_response:\n{gpt_response}")
        answer, etf_list = parse_gpt_response(gpt_response)

    # 결과 표시

    st.subheader("🔍 구글 검색어")
    st.info(search_query)

    # st.subheader(f"📝 구글 검색결과 (status={status_code}, urls={len(urls)})")
    # st.subheader(f"📝 구글 검색결과")
    # st.write(combined_text)
    #st.write(response.json())
    with st.expander("🔽 구글 검색결과 자세히 보기"):
        st.write(combined_text)

    st.subheader("🔖 상담 답변")
    st.info(answer)

    st.subheader(f"📌 추천 ETF ({etf_count}개 요청 -> {len(etf_list)}개 검출)")
    for name, ticker in etf_list:
        # link = f"https://finance.naver.com/search/searchList.naver?query={ticker}"
        link = f"https://finance.naver.com/item/main.naver?code={ticker}"
        
        st.markdown(f"- [{name} ({ticker})]({link})", unsafe_allow_html=True)
