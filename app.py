import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from languages import LANGUAGES
from etf_data import ETF_LIST

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

lang = LANGUAGES[st.session_state.language]

# Add page title
st.markdown("""
    <h1 style='
        text-align: center;
        color: #1f2937;
        margin: 1rem 0;
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
for i, symbol in enumerate(list(ETF_LIST.keys())[:25]):
    with cols[i % 3]:
        try:
            st.markdown('<div class="etf-card">', unsafe_allow_html=True)
            
            etf = yf.Ticker(symbol)
            hist = etf.history(period=lang['periods'][period])
            
            if not hist.empty:
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
            
            st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading {symbol}: {str(e)}")

# Last update time at the bottom
st.caption(f"{lang['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")