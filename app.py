import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from languages import LANGUAGES
from etf_data import ETF_LIST

# CSS 파일 로드
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 페이지 설정
st.set_page_config(
    layout="wide",
    page_title="ETF Tracker",
    page_icon="📈",
    initial_sidebar_state="collapsed"
)

# CSS 로드
load_css()

# 모바일 감지
def is_mobile():
    import streamlit as st
    return st.session_state.get('mobile_browser', False)

# session state initialize
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# sidebar config
with st.sidebar:
    # previous language
    previous_language = st.session_state.language
    
    # language selector
    selected_language = st.selectbox(
        'Language / 언어 / 语言 / 言語 / Idioma',
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key='language_selector'
    )
    
    # update session state if language is changed
    if selected_language != previous_language:
        st.session_state.language = selected_language
        st.rerun()

    lang = LANGUAGES[st.session_state.language]
    
    st.header(lang['settings'])
    
    # 기간 선택 - 기본값을 1개월로 설정
    period_options = list(lang['periods'].keys())
    default_period_index = period_options.index([k for k in period_options if '1' in k and 'M' in k.upper()][0])
    
    period = st.selectbox(
        lang['period'],
        options=period_options,
        index=default_period_index  # 1개월을 기본값으로 설정
    )
    
    chart_type = st.radio(
        lang['chart_type'],
        [lang['candlestick'], lang['line']]
    )

# main title
st.title(lang['title'])

# chart display
if is_mobile():
    cols = st.columns(1)  # 모바일에서는 1열로
else:
    cols = st.columns(3)  # 데스크톱에서는 3열로

for i, symbol in enumerate(list(ETF_LIST.keys())[:6]):
    with cols[i % (1 if is_mobile() else 3)]:
        try:
            # 모바일일 때 구분선 추가 (첫 번째 항목 제외)
            if is_mobile() and i > 0:
                st.markdown("""
                    <hr style="height:2px;border-width:0;color:gray;background-color:#f0f0f0;margin:25px 0;">
                """, unsafe_allow_html=True)
            
            etf = yf.Ticker(symbol)
            hist = etf.history(period=lang['periods'][period])
            
            if hist.empty:
                st.error(f"No data available for {symbol}")
                continue
            
            # 차트 생성
            fig = go.Figure()
            if chart_type == lang['candlestick']:
                fig.add_candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close']
                )
            else:
                fig.add_scatter(
                    x=hist.index,
                    y=hist['Close'],
                    mode='lines'
                )
            
            # 모바일일 때와 데스크톱일 때 다른 레이아웃 적용
            if is_mobile():
                fig.update_layout(
                    title=f'{symbol} - {ETF_LIST[symbol]}',
                    height=300,
                    margin=dict(l=10, r=10, t=40, b=20),
                    showlegend=False,
                    xaxis_rangeslider_visible=False,  # 모바일에서는 하단 작은 그래프 제거
                )
            else:
                fig.update_layout(
                    title=f'{symbol} - {ETF_LIST[symbol]}',
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    template="plotly_white"
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 메트릭 표시
            metrics_cols = st.columns(3)
            current_price = hist['Close'].iloc[-1]
            price_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
            
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

# 모바일에서 마지막 업데이트 시간 위치 조정
if is_mobile():
    st.markdown(f"<p class='small-font'>{lang['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("---")
    st.sidebar.info(f"{lang['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")