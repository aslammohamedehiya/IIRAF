import pandas as pd
import json

# Load the Excel file
xls = pd.ExcelFile(r'C:\Users\pawza\Downloads\additional isues.xlsx')

print("=" * 80)
print("EXCEL FILE ANALYSIS")
print("=" * 80)
print(f"\nSheet names: {xls.sheet_names}\n")

for sheet_name in xls.sheet_names:
    print("\n" + "=" * 80)
    print(f"SHEET: {sheet_name}")
    print("=" * 80)
    
    df = pd.read_excel(xls, sheet_name)
    
    print(f"\nShape: {df.shape} (rows x columns)")
    print(f"\nColumns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\nData Types:")
    print(df.dtypes)
    
    print(f"\nFirst 5 rows:")
    print(df.head(5).to_string())
    
    print(f"\nSample data (row 0):")
    if len(df) > 0:
        for col in df.columns:
            print(f"  {col}: {df[col].iloc[0]}")
    
    print(f"\nNull values:")
    print(df.isnull().sum())
    
    print("\n")
