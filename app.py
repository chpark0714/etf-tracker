import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from languages import LANGUAGES
from etf_data import ETF_LIST

# 페이지 설정
st.set_page_config(
    layout="wide",
    page_title="ETF Tracker",
    page_icon="📈",
    initial_sidebar_state="collapsed"
)

# CSS 수정
st.markdown("""
<style>
    /* 모바일 스타일 */
    @media (max-width: 640px) {
        /* 전체 배경 */
        .main {
            background-color: #f5f5f5;
        }
        
        /* 차트 컨테이너 */
        div.etf-card {
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        /* 차트 여백 조정 */
        .js-plotly-plot {
            height: 300px !important;
            margin-bottom: 70px !important;
        }
        
        /* 메트릭 컨테이너 */
        div.metrics-container {
            background: linear-gradient(to right, #f8f9fa, #ffffff, #f8f9fa);
            padding: 12px;
            border-radius: 8px;
            margin-top: 40px !important;
            border: 1px solid rgba(0,0,0,0.05);
            position: relative;
            z-index: 1;
        }
        
        /* Plotly 차트 컨테이너 추가 여백 */
        .plot-container.plotly {
            margin-bottom: 80px !important;
        }
        
        /* x축 레이블 여백 확보 */
        .xtick {
            margin-bottom: 20px !important;
        }
        
        /* 구분선 스타일 */
        div.etf-divider {
            height: 20px;
            margin: 15px 0;
            opacity: 0.5;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
        }
        
        div.etf-divider::after {
            content: "•••";
            color: #ccc;
            letter-spacing: 2px;
            font-size: 12px;
        }
        
        /* 메트릭 스타일링 */
        .stMetric {
            background: rgba(255,255,255,0.7);
            border-radius: 6px;
            padding: 8px !important;
            border: 1px solid rgba(0,0,0,0.03);
            margin-top: 5px !important;
        }
        
        /* 스트림릿 기본 여백 제거 */
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* 열 사이 여백 제거 */
        .row-widget {
            margin: 0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

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
        st.rerun()

    lang = LANGUAGES[st.session_state.language]
    
    st.header(lang['settings'])
    period = st.selectbox(
        lang['period'],
        options=list(lang['periods'].keys()),
        index=2  # 1개월을 기본값으로
    )
    
    chart_type = st.radio(
        lang['chart_type'],
        [lang['candlestick'], lang['line']]
    )

# 화면 분할 (데스크톱에서는 3열, 모바일에서는 1열)
cols = st.columns(3)

# ETF 표시
for i, symbol in enumerate(list(ETF_LIST.keys())[:6]):
    with cols[i % 3]:
        try:
            # 구분선 먼저 추가 (첫 번째 항목 제외)
            if i > 0:
                st.markdown('<div class="etf-divider"></div>', unsafe_allow_html=True)
            
            # 카드 시작
            st.markdown('<div class="etf-card">', unsafe_allow_html=True)
            
            etf = yf.Ticker(symbol)
            hist = etf.history(period=lang['periods'][period])
            
            if not hist.empty:
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
                
                # 차트 레이아웃
                fig.update_layout(
                    title=f'{symbol} - {ETF_LIST[symbol]}',
                    height=400,
                    margin=dict(l=10, r=10, t=40, b=60),
                    xaxis_rangeslider_visible=False,
                    template="plotly_white",
                    xaxis=dict(
                        tickangle=0,
                        tickfont=dict(size=10),
                        ticktext=hist.index,
                        dtick="M1",
                        tickformat="%Y-%m-%d"
                    ),
                    yaxis=dict(
                        side='right',
                        tickformat=".2f"
                    )
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
            
            # 카드 종료
            st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading {symbol}: {str(e)}")

# 마지막 업데이트 시간
st.sidebar.markdown("---")
st.sidebar.info(f"{lang['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")