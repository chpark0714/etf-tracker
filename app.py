import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import logging
from languages import LANGUAGES
from etf_data import ETF_LIST

# Logging 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Rate Limiter 클래스
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def can_request(self) -> bool:
        now = datetime.now()
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

# 데이터 fetching 함수
@st.cache_data(ttl=300)
def fetch_stock_data(symbol: str, period: str):
    try:
        etf = yf.Ticker(symbol)
        return etf.history(period=period)
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

# ETF 데이터 조회 함수
def get_etf_data(symbol: str, period: str):
    cache_key = f"{symbol}_{period}"
    
    # 캐시 확인
    if cache_key in st.session_state:
        cached_data = st.session_state[cache_key]
        if datetime.now() - cached_data['timestamp'] < timedelta(minutes=5):
            return cached_data['data']

    # 요청 제한 확인
    if not st.session_state.rate_limiter.can_request():
        st.warning("Too many requests. Please wait a moment.")
        time.sleep(2)
        return None

    # 데이터 가져오기
    data = fetch_stock_data(symbol, period)
    
    # 캐시 업데이트
    if data is not None:
        st.session_state[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    return data

# Page configuration
st.set_page_config(
    layout="wide",
    page_title="ETF Tracker",
    page_icon="📈"
)

# Load CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'rate_limiter' not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=50, time_window=60)
if 'error_count' not in st.session_state:
    st.session_state.error_count = 0

lang = LANGUAGES[st.session_state.language]

# Page title
st.markdown("""
    <h1 style='
        text-align: center;
        color: #1f2937;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 1rem 0;
        padding: 0.5rem;
    '>
        📈 ETF Tracker
    </h1>
""", unsafe_allow_html=True)

# Top settings bar
settings_col1, settings_col2, settings_col3 = st.columns([1, 1, 2])

with settings_col1:
    selected_language = st.selectbox(
        'Language',
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language)
    )
    
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()

with settings_col2:
    period = st.selectbox(
        lang['period'],
        options=list(lang['periods'].keys()),
        index=2
    )

# Create columns for ETF layout
cols = st.columns(3)

# Display ETFs
try:
    for i, symbol in enumerate(list(ETF_LIST.keys())[:25]):
        with cols[i % 3]:
            try:
                st.markdown('<div class="etf-card">', unsafe_allow_html=True)
                
                # Get ETF data with rate limiting
                hist = get_etf_data(symbol, lang['periods'][period])
                
                if hist is not None and not hist.empty:
                    # Create chart
                    fig = go.Figure()
                    fig.add_candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close']
                    )
                    
                    # Chart layout
                    fig.update_layout(
                        title=f'{symbol} - {ETF_LIST[symbol]}',
                        title_x=0.5,
                        height=400,
                        margin=dict(l=5, r=5, t=30, b=60),
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
                    
                    # Display metrics
                    metrics_cols = st.columns(3)
                    current_price = hist['Close'].iloc[-1]
                    price_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                    
                    metrics_cols[0].metric(
                        lang['current_price'],
                        f"${current_price:.2f}",
                        f"{price_change:+.2f}%"
                    )
                    metrics_cols[1].metric(
                        lang['volume'],
                        f"{hist['Volume'].iloc[-1]:,.0f}"
                    )
                    metrics_cols[2].metric(
                        lang['high'],
                        f"${hist['High'].iloc[-1]:.2f}"
                    )
                else:
                    st.error(f"No data available for {symbol}")
                    st.session_state.error_count += 1
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                logging.error(f"Error processing {symbol}: {str(e)}")
                st.error(f"Error loading {symbol}")
                st.session_state.error_count += 1
                
            # Check error count
            if st.session_state.error_count >= 3:
                st.error("Too many errors occurred. Please try again later.")
                st.stop()

except Exception as e:
    logging.error(f"Unexpected error: {str(e)}")
    st.error("An unexpected error occurred. Please try again later.")

# Display last update time
st.caption(f"{lang['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")