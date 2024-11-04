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

# CSS 적용
st.markdown("""
<style>
    /* 모바일 스타일 */
    @media (max-width: 640px) {
        /* 차트 컨테이너 */
        div.etf-card {
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* 구분선 */
        div.etf-divider {
            height: 20px;
            margin: 10px -15px;
            background-color: #f5f5f5;
            border-top: 1px solid #e0e0e0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        /* 메트릭 컨테이너 */
        div.metrics-container {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        /* 차트 크기 조정 */
        .js-plotly-plot {
            height: 300px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 화면 너비 계산을 위한 JavaScript 추가
st.markdown("""
<script>
    // 화면 너비를 세션 상태에 저장
    if (window.innerWidth <= 640) {
        window.mobile = true;
    } else {
        window.mobile = false;
    }
</script>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# 사이드바 설정
with st.sidebar:
    # ... (사이드바 코드는 동일)
    pass

# 화면 분할 (데스크톱에서는 3열, 모바일에서는 1열)
use_container_width = True
cols = st.columns(3)  # 기본적으로 3열로 설정

# ETF 표시
for i, symbol in enumerate(list(ETF_LIST.keys())[:6]):
    with cols[i % 3]:  # 3열로 순환
        try:
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
                    height=400,  # 데스크톱에서는 더 큰 높이
                    margin=dict(l=10, r=10, t=40, b=20),
                    xaxis_rangeslider_visible=True,  # 데스크톱에서는 슬라이더 표시
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
            
            st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading {symbol}: {str(e)}")