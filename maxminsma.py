import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Función para cargar datos
@st.cache
def load_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)
    df.reset_index(inplace=True)
    return df

# Aplicación de Streamlit
st.title("Análisis de Precios de Acciones con Máximo/Mínimo y SMA")
st.sidebar.header("Entrada del Usuario")

# Campos de entrada del usuario
ticker = st.sidebar.text_input("Símbolo de la acción", value="AAPL")
start_date = st.sidebar.date_input("Fecha de inicio", value=datetime(2020, 1, 1), min_value=datetime(1990, 1, 1))
end_date = st.sidebar.date_input("Fecha de fin", value=datetime.today(), min_value=datetime(1990, 1, 1))

# Deslizador para el SMA fuera del bloque del botón para mantenerlo visible
sma_period = st.sidebar.slider("Periodo del SMA", min_value=1, max_value=200, value=20)

# Botón para aplicar cambios
if st.sidebar.button("Aplicar"):
    # Cargar datos
    df = load_data(ticker, start_date, end_date)

    # Mostrar datos y gráfico
    st.subheader(f"Datos de precios para {ticker} desde {start_date} hasta {end_date}")
    st.write(df.head())

    # Gráfico de precios con SMA ajustable
    st.subheader("Gráfico de Precios con Máximo/Mínimo y SMA")
    
    # Gráficar con Plotly
    fig = go.Figure()

    # Agregar línea de precio
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name="Precio"))

    # Agregar líneas de máximo y mínimo
    fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], mode='lines', name="Valor Máximo", line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], mode='lines', name="Valor Mínimo", line=dict(color='red')))

    # Agregar SMA
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()
    fig.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['SMA'], 
        mode='lines', 
        name=f"SMA {sma_period}",
        line=dict(color='yellow')  # Configurar el color de la línea a amarillo
    ))

    fig.update_layout(title=f"Gráfico de Precios de {ticker}",
                      xaxis_title="Fecha",
                      yaxis_title="Precio (USD)",
                      xaxis_rangeslider_visible=False)

    st.plotly_chart(fig)

    # Ratio de Máximo/Mínimo con SMA y Promedio
    st.subheader("Ratio de Máximo/Mínimo con SMA y Promedio")
    df['Ratio'] = df['High'] / df['Low']
    df['SMA_Ratio'] = df['Ratio'].rolling(window=sma_period).mean()
    average_ratio = df['Ratio'].mean()

    fig_ratio = go.Figure()

    # Agregar línea de Ratio
    fig_ratio.add_trace(go.Scatter(x=df['Date'], y=df['Ratio'], mode='lines', name="Ratio Máximo/Mínimo"))

    # Agregar SMA del Ratio
    fig_ratio.add_trace(go.Scatter(x=df['Date'], y=df['SMA_Ratio'], mode='lines', name=f"SMA {sma_period} del Ratio"))

    # Agregar línea de promedio
    fig_ratio.add_trace(go.Scatter(x=df['Date'], y=[average_ratio]*len(df), mode='lines', name="Promedio del Ratio", line=dict(color='green', dash='dash')))

    fig_ratio.update_layout(title=f"Ratio Máximo/Mínimo de {ticker} con SMA y Promedio",
                            xaxis_title="Fecha",
                            yaxis_title="Ratio",
                            xaxis_rangeslider_visible=False)

    st.plotly_chart(fig_ratio)

    # Tercer gráfico: SMA y relación de Precio/SMA
    st.subheader("Gráfico de SMA y Relación Precio/SMA")
    df['Precio/SMA'] = df['Close'] / df['SMA']

    fig_price_sma_ratio = go.Figure()

    # Agregar SMA del Precio
    fig_price_sma_ratio.add_trace(go.Scatter(x=df['Date'], y=df['SMA'], mode='lines', name=f"SMA {sma_period}", line=dict(color='yellow')))

    # Agregar Relación Precio/SMA
    fig_price_sma_ratio.add_trace(go.Scatter(x=df['Date'], y=df['Precio/SMA'], mode='lines', name="Precio/SMA", line=dict(color='blue')))

    fig_price_sma_ratio.update_layout(title=f"SMA y Relación Precio/SMA de {ticker}",
                                      xaxis_title="Fecha",
                                      yaxis_title="Valor",
                                      xaxis_rangeslider_visible=False)

    st.plotly_chart(fig_price_sma_ratio)
