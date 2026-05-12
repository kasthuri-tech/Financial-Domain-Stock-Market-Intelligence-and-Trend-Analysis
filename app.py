import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. SETUP & CONFIGURATION ---
# This sets the page title and makes the layout wide for better charts
st.set_page_config(page_title="Nifty 50 Stock Analysis", layout="wide")

# This automatically finds the database file in your project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stock_analysis.db")

# --- 2. REUSABLE DATABASE FUNCTIONS ---
# This function connects to the SQL database
def get_connection():
    return sqlite3.connect(DB_PATH)

# This REUSABLE function runs any SQL query and returns a Pandas DataFrame
@st.cache_data
def load_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- 3. SIDEBAR NAVIGATION ---
# This creates the menu on the left side of your dashboard
st.sidebar.title("🏛️ Project Navigation")
menu = st.sidebar.radio("Go to:", [
    "Market Overview", 
    "Volatility Analysis", 
    "Cumulative Returns", 
    "Sector Performance", 
    "Stock Correlation", 
    "Monthly Trends"
])

# Displays the title based on what menu item is selected
st.title(f"🚀 Nifty 50 Analysis: {menu}")

# --- SEGMENT 1: MARKET OVERVIEW ---
if menu == "Market Overview":
    st.subheader("Key Market Metrics")
    
    # STEP 1: Get all data from the 'nifty50_data' SQL table
    df_all = load_data("SELECT * FROM nifty50_data")
    df_all['date'] = pd.to_datetime(df_all['date'])
    
    # STEP 2: Loop through each stock to calculate Yearly Returns
    summary = []
    for ticker in df_all['Ticker'].unique():
        ticker_df = df_all[df_all['Ticker'] == ticker].sort_values('date')
        first_price = ticker_df['close'].iloc[0]
        last_price = ticker_df['close'].iloc[-1]
        ret = (last_price - first_price) / first_price
        # Store results in a list
        summary.append({
            'Ticker': ticker, 
            'Return_Pct': ret * 100, 
            'Avg_Price': ticker_df['close'].mean(), 
            'Avg_Vol': ticker_df['volume'].mean()
        })
    
    metrics_df = pd.DataFrame(summary)
    
    # STEP 3: Display the big numbers at the top (Average Price, Volume, etc.)
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Stock Price", f"₹{metrics_df['Avg_Price'].mean():.2f}")
    col2.metric("Average Daily Volume", f"{metrics_df['Avg_Vol'].mean():,.0f}")
    col3.metric("Green vs Red Stocks", f"{len(metrics_df[metrics_df['Return_Pct'] > 0])} G / {len(metrics_df[metrics_df['Return_Pct'] <= 0])} R")

    st.markdown("---")
    colA, colB = st.columns(2)
    
    # STEP 4: Display the Top 10 Gainers and Losers in tables
    with colA:
        st.success("📈 Top 10 Green Stocks")
        st.dataframe(metrics_df.sort_values('Return_Pct', ascending=False).head(10))
        
    with colB:
        st.error("📉 Top 10 Loss Stocks")
        st.dataframe(metrics_df.sort_values('Return_Pct', ascending=True).head(10))

# --- SEGMENT 2: VOLATILITY ANALYSIS ---
elif menu == "Volatility Analysis":
    st.subheader("Volatility of Top 10 Most Volatile Stocks")
    
    # STEP 1: Fetch data from SQL
    df_all = load_data("SELECT * FROM nifty50_data")
    vols = []
    # STEP 2: Calculate daily returns and Standard Deviation for every stock
    for ticker in df_all['Ticker'].unique():
        t_df = df_all[df_all['Ticker'] == ticker].sort_values('date')
        t_df['ret'] = t_df['close'].pct_change()
        vols.append({'Ticker': ticker, 'Volatility': t_df['ret'].std()})
    
    # STEP 3: Select only the top 10 most volatile
    vol_df = pd.DataFrame(vols).sort_values('Volatility', ascending=False).head(10)
    
    # STEP 4: Create a professional Bar Chart using Plotly
    fig = px.bar(vol_df, x='Ticker', y='Volatility', color='Volatility', title="Top 10 Volatile Stocks")
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 High volatility indicates more risk, while low volatility indicates stability.")

# --- SEGMENT 3: CUMULATIVE RETURNS ---
elif menu == "Cumulative Returns":
    st.subheader("Growth of Top 5 Performing Stocks")
    
    df_all = load_data("SELECT * FROM nifty50_data")
    df_all['date'] = pd.to_datetime(df_all['date'])
    
    # STEP 1: Find the Top 5 stocks by total growth
    performance = []
    for t in df_all['Ticker'].unique():
        prices = df_all[df_all['Ticker'] == t].sort_values('date')['close']
        performance.append({'Ticker': t, 'Total_Return': (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]})
    
    top_5_tickers = pd.DataFrame(performance).sort_values('Total_Return', ascending=False).head(5)['Ticker'].tolist()
    
    # STEP 2: Create a Line Chart showing how these 5 stocks grew over time
    fig = go.Figure()
    for t in top_5_tickers:
        t_df = df_all[df_all['Ticker'] == t].sort_values('date')
        # This formula calculates the 'Running Total' of returns
        t_df['cum_ret'] = (1 + t_df['close'].pct_change().fillna(0)).cumprod()
        fig.add_trace(go.Scatter(x=t_df['date'], y=t_df['cum_ret'], mode='lines', name=t))
    
    fig.update_layout(title="Cumulative Return Growth", xaxis_title="Date", yaxis_title="Growth (Base 1.0)")
    st.plotly_chart(fig, use_container_width=True)

# --- SEGMENT 4: SECTOR PERFORMANCE ---
elif menu == "Sector Performance":
    st.subheader("Average Yearly Return by Industry Sector")
    
    # STEP 1: Use a SQL JOIN to combine Stock data with Sector Mapping
    query = """
    SELECT n.Ticker, s.sector, n.close, n.date 
    FROM nifty50_data n 
    JOIN sector_mapping s ON n.Ticker = s.Ticker
    """
    df_sector = load_data(query)
    df_sector['date'] = pd.to_datetime(df_sector['date'])
    
    # STEP 2: Calculate the average return for each group (Sector)
    sector_res = []
    for s in df_sector['sector'].unique():
        s_df = df_sector[df_sector['sector'] == s]
        stock_rets = []
        for t in s_df['Ticker'].unique():
            t_prices = s_df[s_df['Ticker'] == t].sort_values('date')['close']
            stock_rets.append((t_prices.iloc[-1] - t_prices.iloc[0]) / t_prices.iloc[0])
        sector_res.append({'Sector': s, 'Avg_Return': sum(stock_rets)/len(stock_rets) * 100})
    
    sec_df = pd.DataFrame(sector_res).sort_values('Avg_Return', ascending=False)
    # STEP 3: Show Sector-wise performance in a Bar Chart
    fig = px.bar(sec_df, x='Sector', y='Avg_Return', color='Avg_Return', title="Sector-wise Average Return (%)")
    st.plotly_chart(fig, use_container_width=True)

# --- SEGMENT 5: STOCK CORRELATION ---
elif menu == "Stock Correlation":
    st.subheader("Price Correlation Heatmap (Top 10 Stocks)")
    
    # STEP 1: Extract price data for the first 10 stocks
    df_all = load_data("SELECT * FROM nifty50_data")
    top_10 = df_all['Ticker'].unique()[:10]
    
    corr_data = {}
    for t in top_10:
        corr_data[t] = df_all[df_all['Ticker'] == t].sort_values('date')['close'].values
    
    # STEP 2: Calculate the Correlation Matrix (using Pandas)
    corr_matrix = pd.DataFrame(corr_data).corr()
    
    # STEP 3: Use SEABORN to paint the colorful Heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', ax=ax)
    st.pyplot(fig)

# --- SEGMENT 6: MONTHLY TRENDS ---
elif menu == "Monthly Trends":
    st.subheader("Top 5 Gainers & Losers (By Month)")
    
    df_all = load_data("SELECT * FROM nifty50_data")
    df_all['date'] = pd.to_datetime(df_all['date'])
    df_all['month'] = df_all['date'].dt.strftime('%Y-%m')
    
    # STEP 1: Create a Dropdown box for the user to select a month
    selected_month = st.selectbox("Select Month", sorted(df_all['month'].unique(), reverse=True))
    
    # STEP 2: Filter data for that specific month
    m_df = df_all[df_all['month'] == selected_month]
    monthly_rets = []
    for t in m_df['Ticker'].unique():
        t_prices = m_df[m_df['Ticker'] == t].sort_values('date')['close']
        monthly_rets.append({'Ticker': t, 'Return': (t_prices.iloc[-1] - t_prices.iloc[0]) / t_prices.iloc[0] * 100})
    
    res_df = pd.DataFrame(monthly_rets)
    
    # STEP 3: Display two tables: one for Gainers and one for Losers
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"📈 Top 5 Gainers in {selected_month}")
        st.dataframe(res_df.sort_values('Return', ascending=False).head(5))
    with col2:
        st.error(f"📉 Top 5 Losers in {selected_month}")
        st.dataframe(res_df.sort_values('Return', ascending=True).head(5))
