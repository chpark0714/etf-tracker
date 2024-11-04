import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from languages import LANGUAGES
from etf_data import ETF_LIST  # ETF 목록 import

# 페이지 설정
st.set_page_config(layout="wide")

# 세션 상태 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# 사이드바 설정
with st.sidebar:
    # 이전 언어 저장
    previous_language = st.session_state.language
    
    # 언어 선택
    selected_language = st.selectbox(
        'Language / 언어 / 语言 / 言語 / Idioma',
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key='language_selector'
    )
    
    # 언어가 변경되었을 때만 세션 상태 업데이트
    if selected_language != previous_language:
        st.session_state.language = selected_language
        st.rerun()  # experimental_rerun() 대신 rerun() 사용

    lang = LANGUAGES[st.session_state.language]
    
    st.header(lang['settings'])
    period = st.selectbox(
        lang['period'],
        options=list(lang['periods'].keys())
    )
    
    chart_type = st.radio(
        lang['chart_type'],
        [lang['candlestick'], lang['line']]
    )

# 메인 타이틀
st.title(lang['title'])

# 차트 표시
cols = st.columns(3)
for i, symbol in enumerate(ETF_LIST.keys()):
    with cols[i % 3]:
        try:
            etf = yf.Ticker(symbol)
            hist = etf.history(period=lang['periods'][period])
            
            if chart_type == lang['candlestick']:
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close']
                )])
            else:
                fig = go.Figure(data=[go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    mode='lines'
                )])
            
            fig.update_layout(
                title=f'{symbol} - {ETF_LIST[symbol]}',
                height=400,
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 메트릭 표시
            metrics_cols = st.columns(3)
            current_price = hist['Close'].iloc[-1]
            price_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            
            metrics_cols[0].metric(
                lang['current_price'],
                f"${current_price:.2f}",
                f"{price_change:.2f}%"
            )
            metrics_cols[1].metric(
                lang['volume'],
                f"{hist['Volume'].iloc[-1]:,.0f}"
            )
            metrics_cols[2].metric(
                lang['high'],
                f"${hist['High'].iloc[-1]:.2f}"
            )
            
        except Exception as e:
            st.error(f"Error loading {symbol}: {str(e)}")

# 마지막 업데이트 시간
st.sidebar.markdown("---")
st.sidebar.info(f"{lang['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")