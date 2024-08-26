import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Set the title of the app
st.title("Max/Min Values with Ratio and SMA")

# User inputs for stock ticker, SMA length, and date range
ticker = st.text_input("Enter stock ticker:", "AAPL").upper()
sma_length = st.slider("Select SMA length for the price chart:", min_value=1, max_value=50, value=14)
start_date = st.date_input("Start date:", value=pd.to_datetime("2022-01-01"))
end_date = st.date_input("End date:", value=datetime.today())

# Button to fetch and process data
if st.button("Enter"):
    # Load the data
    @st.cache
    def load_data(ticker, start, end):
        df = yf.download(ticker, start=start, end=end)
        return df

    df = load_data(ticker, start_date, end_date)

    # Calculate daily high and low
    df['Daily High'] = df['High'].resample('D').transform('max')
    df['Daily Low'] = df['Low'].resample('D').transform('min')

    # Calculate ratio and SMA of the ratio
    df['Ratio'] = df['Daily High'] / df['Daily Low']
    df['SMA'] = df['Ratio'].rolling(window=sma_length).mean()

    # Calculate SMA for the price chart
    df['SMA Price'] = df['Close'].rolling(window=sma_length).mean()

    # Plot the price chart with max and min values and SMA
    fig_price = go.Figure()

    fig_price.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))

    fig_price.add_trace(go.Scatter(
        x=df.index,
        y=df['Daily High'],
        mode='lines',
        name='Daily High',
        line=dict(color='green')
    ))

    fig_price.add_trace(go.Scatter(
        x=df.index,
        y=df['Daily Low'],
        mode='lines',
        name='Daily Low',
        line=dict(color='red')
    ))

    fig_price.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA Price'],
        mode='lines',
        name=f'SMA ({sma_length}) of Price',
        line=dict(color='purple')
    ))

    fig_price.update_layout(title=f'{ticker} Price Chart with Daily High, Low, and SMA',
                            xaxis_title='Date',
                            yaxis_title='Price',
                            xaxis_rangeslider_visible=False)

    st.plotly_chart(fig_price)

    # Plot the ratio and SMA
    fig_ratio = go.Figure()

    fig_ratio.add_trace(go.Scatter(
        x=df.index,
        y=df['Ratio'],
        mode='lines',
        name='Max/Min Ratio',
        line=dict(color='blue')
    ))

    fig_ratio.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA'],
        mode='lines',
        name=f'SMA ({sma_length}) of Ratio',
        line=dict(color='orange')
    ))

    fig_ratio.update_layout(title='Ratio of Max/Min Values and SMA',
                            xaxis_title='Date',
                            yaxis_title='Ratio')

    st.plotly_chart(fig_ratio)
