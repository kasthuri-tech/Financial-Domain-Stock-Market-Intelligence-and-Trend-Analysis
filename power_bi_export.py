import pandas as pd
import sqlite3
import os

def export_for_powerbi():
    # 1. Setup paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "stock_analysis.db")
    OUTPUT_FILE = os.path.join(BASE_DIR, "Test data", "Nifty50_Master_for_PowerBI.csv")
    
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Please run database_loader.py first.")
        return

    # 2. Connect and Join Data
    conn = sqlite3.connect(DB_PATH)
    
    # We JOIN the stock data with the sector mapping so Power BI has everything in one file
    query = """
    SELECT n.*, s.sector, s.COMPANY 
    FROM nifty50_data n
    JOIN sector_mapping s ON n.Ticker = s.Ticker
    """
    
    df_master = pd.read_sql(query, conn)
    conn.close()
    
    # 3. Save the final file
    df_master.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\nSUCCESS! 🏛️🏁")
    print(f"Master file created at: {OUTPUT_FILE}")
    print("You can now import this single file into Power BI for your final dashboard!")

if __name__ == "__main__":
    export_for_powerbi()
