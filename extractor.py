import yaml
import pandas as pd
import os
from glob import glob

def extract_and_concat_stock_data(base_path, output_folder):
    all_dfs = []
    
    # Path to the folders containing the months (Updated to local Test data folder)
    # This matches the structure: Test data/original_yamls/2023-10, etc.
    path_month = [
        "2023-10", "2023-11", "2023-12", 
        "2024-01", "2024-02", "2024-03", 
        "2024-04", "2024-05", "2024-06", 
        "2024-07", "2024-08", "2024-09", 
        "2024-10", "2024-11"
    ]
    
    print("Starting Demo Extraction using local 'Test data'...")
    
    # Step 2: Nested Loops (Month -> Files)
    for month in path_month:
        month_path = os.path.join(base_path, month)
        
        # Get all YAML files for this specific month
        path_date = glob(os.path.join(month_path, "*.yaml"))
        
        for file_path in path_date:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Load YAML and convert to DataFrame
                raw_data = yaml.safe_load(file)
                temp_df = pd.DataFrame(raw_data)
                all_dfs.append(temp_df)
                
        print(f"Loaded month: {month}")

    # Step 3: Concat all data into 'wholedf'
    wholedf = pd.concat(all_dfs, ignore_index=True)
    
    # Step 4: Reorder columns [date, open, high, low, close, volume, Ticker]
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'Ticker']
    wholedf = wholedf[cols]
    
    # Step 5: Save based on Ticker name into nifty50_data folder
    tickers = wholedf['Ticker'].unique()
    for symbol in tickers:
        symbol_df = wholedf[wholedf['Ticker'] == symbol].sort_values(by='date')
        file_name = f"{symbol}.csv"
        symbol_df.to_csv(os.path.join(output_folder, file_name), index=False)

    print(f"\nSUCCESS! 50 CSVs generated in the '{os.path.basename(output_folder)}' folder.")

if __name__ == "__main__":
    # PROFESSIONAL WAY: Use relative paths based on script location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_PATH = os.path.join(BASE_DIR, "Test data", "original_yamls")
    FINAL_PATH = os.path.join(BASE_DIR, "Test data", "nifty50_data")
    
    if not os.path.exists(FINAL_PATH):
        os.makedirs(FINAL_PATH)
        
    extract_and_concat_stock_data(RAW_PATH, FINAL_PATH)
