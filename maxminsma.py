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
ticker_input = st.sidebar.text_input("Símbolo(s) de la acción (separados por comas)", value="AAPL")
tickers = [t.strip() for t in ticker_input.upper().split(',')]
start_date = st.sidebar.date_input("Fecha de inicio", value=datetime(2020, 1, 1), min_value=datetime(1990, 1, 1))
end_date = st.sidebar.date_input("Fecha de fin", value=datetime.today(), min_value=datetime(1990, 1, 1))

# Deslizador para el SMA fuera del bloque del botón para mantenerlo visible
sma_period = st.sidebar.slider("Periodo del SMA", min_value=1, max_value=200, value=20)

# Botón para aplicar cambios
if st.sidebar.button("Aplicar"):
  data = {}

  # Cargar datos para cada ticker
  for ticker in tickers:
      df = load_data(ticker, start_date, end_date)
      if not df.empty:
          data[ticker] = df
      else:
          st.warning(f"No se encontraron datos para el símbolo {ticker}")

  if data:
      # Gráfico de precios con SMA ajustable (opcional para un solo ticker)
      if len(tickers) == 1:
          df = data[tickers[0]]
          st.subheader(f"Datos de precios para {tickers[0]} desde {start_date} hasta {end_date}")
          st.write(df.head())

          st.subheader("Gráfico de Precios con Máximo/Mínimo y SMA")
          
          # Graficar con Plotly
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

          fig.update_layout(title=f"Gráfico de Precios de {tickers[0]}",
                            xaxis_title="Fecha",
                            yaxis_title="Precio (USD)",
                            xaxis_rangeslider_visible=False)

          st.plotly_chart(fig)
      else:
          st.subheader("Múltiples símbolos detectados, omitiendo el gráfico de precios individuales.")

      # Ratio de Máximo/Mínimo con SMA y Promedio
      st.subheader("Ratio de Máximo/Mínimo con SMA y Promedio")

      fig_ratio = go.Figure()
      
      # Colores para distinguir cada ticker
      colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
      
      for idx, ticker in enumerate(data):
          df = data[ticker].copy()
          df['Ratio'] = df['High'] / df['Low']
          df['SMA_Ratio'] = df['Ratio'].rolling(window=sma_period).mean()
          average_ratio = df['Ratio'].mean()

          color = colors[idx % len(colors)]  # Asignar un color

          # Agregar línea de Ratio
          fig_ratio.add_trace(go.Scatter(
              x=df['Date'], 
              y=df['Ratio'], 
              mode='lines', 
              name=f"Ratio {ticker}",
              line=dict(color=color)
          ))

          # Agregar SMA del Ratio
          fig_ratio.add_trace(go.Scatter(
              x=df['Date'], 
              y=df['SMA_Ratio'], 
              mode='lines', 
              name=f"SMA {sma_period} del Ratio {ticker}",
              line=dict(color=color, dash='dash')
          ))

          # Agregar línea de promedio
          fig_ratio.add_trace(go.Scatter(
              x=df['Date'], 
              y=[average_ratio]*len(df), 
              mode='lines', 
              name=f"Promedio del Ratio {ticker}", 
              line=dict(color=color, dash='dot')
          ))

      fig_ratio.update_layout(title="Ratio Máximo/Mínimo con SMA y Promedio",
                              xaxis_title="Fecha",
                              yaxis_title="Ratio",
                              xaxis_rangeslider_visible=False)

      st.plotly_chart(fig_ratio)

      # Tercer gráfico: SMA del ratio y relación Precio/SMA
      st.subheader("SMA del Ratio y Relación Precio/SMA")

      fig_third = go.Figure()
      for idx, ticker in enumerate(data):
          df = data[ticker].copy()
          df['Ratio'] = df['High'] / df['Low']
          df['SMA_Ratio'] = df['Ratio'].rolling(window=sma_period).mean()
          df['SMA'] = df['Close'].rolling(window=sma_period).mean()
          df['Price/SMA'] = df['Close'] / df['SMA']

          color = colors[idx % len(colors)]  # Asignar un color

          # Agregar SMA del Ratio
          fig_third.add_trace(go.Scatter(
              x=df['Date'], 
              y=df['SMA_Ratio'], 
              mode='lines', 
              name=f"SMA {sma_period} del Ratio {ticker}",
              line=dict(color=color)
          ))

          # Agregar relación Precio/SMA
          fig_third.add_trace(go.Scatter(
              x=df['Date'], 
              y=df['Price/SMA'], 
              mode='lines', 
              name=f"Relación Precio/SMA {ticker}",
              line=dict(color=color, dash='dash')
          ))

      fig_third.update_layout(title="SMA del Ratio y Relación Precio/SMA",
                              xaxis_title="Fecha",
                              yaxis_title="Valor",
                              xaxis_rangeslider_visible=False)

      st.plotly_chart(fig_third)
