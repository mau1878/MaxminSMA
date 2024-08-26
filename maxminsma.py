import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Function to load data
@st.cache
def load_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)
    df.reset_index(inplace=True)
    return df

# Streamlit app
st.title("Stock Price Analysis with Max/Min and SMA")
st.sidebar.header("User Input")

# User input fields
ticker = st.sidebar.text_input("Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start date", value=datetime(2020, 1, 1))
end_date = st.sidebar.date_input("End date", value=datetime.today())

# Button to apply changes
if st.sidebar.button("Enter"):
    # Load data
    df = load_data(ticker, start_date, end_date)

    # Display data and plot
    st.subheader(f"Price data for {ticker} from {start_date} to {end_date}")
    st.write(df.head())

    # Price chart with adjustable SMA
    st.subheader("Price Chart with Max/Min and SMA")
    sma_period = st.sidebar.slider("SMA Period", min_value=1, max_value=100, value=20)

    # Plotting with Plotly
    fig = go.Figure()

    # Add price line
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name="Price"))

    # Add max and min points
    fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], mode='markers', name="Max Value", marker=dict(color='red', size=6)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], mode='markers', name="Min Value", marker=dict(color='blue', size=6)))

    # Add SMA
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA'], mode='lines', name=f"SMA {sma_period}"))

    fig.update_layout(title=f"{ticker} Price Chart",
                      xaxis_title="Date",
                      yaxis_title="Price (USD)",
                      xaxis_rangeslider_visible=False)

    st.plotly_chart(fig)

    # Ratio of Max/Min with SMA
    st.subheader("Ratio of Max/Min with SMA")
    df['Ratio'] = df['High'] / df['Low']
    df['SMA_Ratio'] = df['Ratio'].rolling(window=sma_period).mean()

    fig_ratio = go.Figure()

    # Add Ratio line
    fig_ratio.add_trace(go.Scatter(x=df['Date'], y=df['Ratio'], mode='lines', name="Max/Min Ratio"))

    # Add SMA of Ratio
    fig_ratio.add_trace(go.Scatter(x=df['Date'], y=df['SMA_Ratio'], mode='lines', name=f"SMA {sma_period} of Ratio"))

    fig_ratio.update_layout(title="Max/Min Ratio with SMA",
                            xaxis_title="Date",
                            yaxis_title="Ratio",
                            xaxis_rangeslider_visible=False)

    st.plotly_chart(fig_ratio)
