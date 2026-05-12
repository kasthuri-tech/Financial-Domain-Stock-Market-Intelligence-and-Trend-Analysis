import pandas as pd
import os
from sqlalchemy import create_engine
from glob import glob

def load_data_to_sql():
    # 1. Setup paths using professional relative logic
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "Test data", "nifty50_data")
    SECTOR_FILE = os.path.join(BASE_DIR, "Test data", "Sector_data.csv")
    
    # 2. Create the SQL Engine (using SQLite for the demo)
    # This creates a file named 'stock_analysis.db' in your project folder
    db_path = os.path.join(BASE_DIR, "stock_analysis.db")
    engine = create_engine(f'sqlite:///{db_path}')
    
    print(f"Connecting to database: {db_path}...")

    # 3. Load Sector Data first
    if os.path.exists(SECTOR_FILE):
        sector_df = pd.read_csv(SECTOR_FILE)
        # Clean the ticker name in sector data for better joining
        sector_df['Ticker'] = sector_df['Symbol'].str.split(': ').str[-1].str.strip()
        sector_df.to_sql('sector_mapping', engine, if_exists='replace', index=False)
        print("SUCCESS: Sector Mapping loaded into SQL.")
    else:
        print(f"Warning: Sector file not found at {SECTOR_FILE}")

    # 4. Load the 50 Stock CSVs
    csv_files = glob(os.path.join(DATA_PATH, "*.csv"))
    total_rows = 0
    
    if not csv_files:
        print(f"Error: No CSV files found in {DATA_PATH}. Please run extractor.py first.")
        return

    print(f"Found {len(csv_files)} files. Starting SQL upload...")
    
    for i, file_path in enumerate(csv_files, 1):
        ticker = os.path.basename(file_path).replace('.csv', '')
        df = pd.read_csv(file_path)
        
        # Append all stocks into ONE master table called 'nifty50_data'
        mode = 'replace' if i == 1 else 'append'
        df.to_sql('nifty50_data', engine, if_exists=mode, index=False)
        
        total_rows += len(df)
        if i % 10 == 0:
            print(f"Progress: {i}/50 files loaded...")

    print(f"\nSUCCESS! 🏛️🏁")
    print(f"Total Files Loaded: {len(csv_files)}")
    print(f"Total Rows in Database: {total_rows}")
    print("Your project is now powered by a professional SQL Database!")

if __name__ == "__main__":
    load_data_to_sql()
