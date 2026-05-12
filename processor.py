import pandas as pd
import os
from glob import glob

def get_market_metrics(input_dir):
    all_summary = []
    
    # Step 1: Get all CSV files
    csv_files = glob(os.path.join(input_dir, "*.csv"))
    
    for file_path in csv_files:
        df = pd.read_csv(file_path)
        ticker = os.path.basename(file_path).replace('.csv', '')
        
        # Step 2: Basic Metrics
        # Yearly Return = (Last Close - First Close) / First Close
        first_price = df['close'].iloc[0]
        last_price = df['close'].iloc[-1]
        yearly_return = (last_price - first_price) / first_price
        
        # Step 3: Averages
        avg_price = df['close'].mean()
        avg_volume = df['volume'].mean()
        
        # Step 4: Store in a list
        all_summary.append({
            'Ticker': ticker,
            'Yearly_Return_Pct': yearly_return * 100,
            'Avg_Price': avg_price,
            'Avg_Volume': avg_volume,
            'Status': 'Green' if yearly_return > 0 else 'Red'
        })
    
    return pd.DataFrame(all_summary)

if __name__ == "__main__":
    # PROFESSIONAL WAY: Use relative paths based on the current script location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "Test data", "nifty50_data")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: Path not found -> {DATA_PATH}")
    else:
        # Run the analysis
        metrics_df = get_market_metrics(DATA_PATH)
        
        # Show Top 10 Green Stocks
        print("\n--- TOP 10 GREEN STOCKS ---")
        print(metrics_df.sort_values(by='Yearly_Return_Pct', ascending=False).head(10))
        
        # Show Top 10 Loss Stocks
        print("\n--- TOP 10 LOSS STOCKS ---")
        print(metrics_df.sort_values(by='Yearly_Return_Pct', ascending=True).head(10))
        
        # Market Summary
        green_count = len(metrics_df[metrics_df['Status'] == 'Green'])
        red_count = len(metrics_df[metrics_df['Status'] == 'Red'])
        print(f"\nMarket Summary: {green_count} Green Stocks, {red_count} Red Stocks")
