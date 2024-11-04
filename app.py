import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="ETF 트래커", layout="wide", memory_limit=1024)
st.title("Top 25 ETF 가격 동향")

# ETF 목록
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

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    period = st.selectbox(
        "기간 선택",
        ["1일", "1주일", "1개월", "3개월", "6개월", "1년"],
        index=2
    )
    
    period_map = {
        "1일": "1d",
        "1주일": "1wk",
        "1개월": "1mo",
        "3개월": "3mo",
        "6개월": "6mo",
        "1년": "1y"
    }
    
    chart_type = st.radio(
        "차트 종류",
        ["캔들스틱", "라인"]
    )
    
    selected_etfs = st.multiselect(
        "표시할 ETF 선택",
        list(etf_list.keys()),
        default=list(etf_list.keys())[:6]
    )

# 메인 컨텐츠
cols = st.columns(3)
for i, symbol in enumerate(selected_etfs):
    with cols[i % 3]:
        try:
            etf = yf.Ticker(symbol)
            hist = etf.history(period=period_map[period])
            
            if chart_type == "캔들스틱":
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
                "현재가",
                f"${current_price:.2f}",
                f"{price_change:.2f}%"
            )
            metrics_cols[1].metric(
                "거래량",
                f"{volume:,.0f}"
            )
            metrics_cols[2].metric(
                "고가",
                f"${hist['High'][-1]:.2f}"
            )
            
        except Exception as e:
            st.error(f"{symbol} 데이터 로딩 중 오류 발생")

# 페이지 하단 정보
st.sidebar.markdown("---")

st.sidebar.info(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")