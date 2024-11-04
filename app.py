import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from languages import LANGUAGES

# 페이지 설정
st.set_page_config(layout="wide")

# 세션 상태 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# 사이드바 설정

with st.sidebar:
    # 언어 선택
    selected_language = st.selectbox(
        'Language / 언어 / 语言 / 言語 / Idioma',
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language)
    )
    
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.experimental_rerun()

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

# ETF 목록도 별도 파일로 분리할 수 있습니다
etf_list = {
    'SPY': 'S&P 500 ETF',
    'VOO': 'Vanguard S&P 500',
    'VTI': 'Vanguard Total Stock Market',
    'QQQ': 'Nasdaq 100 ETF',
    'IVV': 'iShares Core S&P 500',
    'BND': 'Vanguard Total Bond Market',
    'VEA': 'Vanguard FTSE Developed Markets',
    'VTV': 'Vanguard Value ETF',
    'AGG': 'iShares Core U.S. Aggregate Bond',
    'VUG': 'Vanguard Growth ETF',
    'IEFA': 'iShares Core MSCI EAFE',
    'VWO': 'Vanguard Emerging Markets',
    'IJR': 'iShares Core S&P Small-Cap',
    'IWF': 'iShares Russell 1000 Growth',
    'IWM': 'iShares Russell 2000',
    'VIG': 'Vanguard Dividend Appreciation',
    'VXUS': 'Vanguard Total International Stock',
    'VGT': 'Vanguard Information Technology',
    'IEMG': 'iShares Core MSCI Emerging Markets',
    'GLD': 'SPDR Gold Shares',
    'LQD': 'iShares iBoxx Investment Grade Corporate Bond',
    'VNQ': 'Vanguard Real Estate',
    'TLT': 'iShares 20+ Year Treasury Bond',
    'IWD': 'iShares Russell 1000 Value',
    'EFA': 'iShares MSCI EAFE'
}

# 메인 타이틀
st.title(LANGUAGES[st.session_state.language]['title'])

# 메인 컨텐츠
cols = st.columns(3)
for i, symbol in enumerate(etf_list.keys()):
    with cols[i % 3]:
        try:
            etf = yf.Ticker(symbol)
            hist = etf.history(period=LANGUAGES[st.session_state.language]['periods'][period])
            
            if chart_type == LANGUAGES[st.session_state.language]['candlestick']:
                fig = go.Figure(data=[go.Candlestick(x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'])])
            else:
                fig = go.Figure(data=[go.Scatter(x=hist.index, 
                    y=hist['Close'],
                    mode='lines',
                    name=symbol)])
            
            fig.update_layout(
                title=f'{symbol} - {etf_list[symbol]}',
                height=400,
                xaxis_title="날짜",
                yaxis_title="가격 (USD)",
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 기본 정보 표시
            current_price = hist['Close'][-1]
            price_change = ((current_price - hist['Close'][0]) / hist['Close'][0]) * 100
            volume = hist['Volume'][-1]
            
            # 메트릭 컨테이너
            metrics_cols = st.columns(3)
            metrics_cols[0].metric(
                LANGUAGES[st.session_state.language]['current_price'],
                f"${current_price:.2f}",
                f"{price_change:.2f}%"
            )
            metrics_cols[1].metric(
                LANGUAGES[st.session_state.language]['volume'],
                f"{volume:,.0f}"
            )
            metrics_cols[2].metric(
                LANGUAGES[st.session_state.language]['high'],
                f"${hist['High'][-1]:.2f}"
            )
            
        except Exception as e:
            st.error(f"{symbol} 데이터 로딩 중 오류 발생")

# 페이지 하단 정보
st.sidebar.markdown("---")

st.sidebar.info(f"{LANGUAGES[st.session_state.language]['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")