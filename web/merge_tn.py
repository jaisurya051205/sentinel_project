import pandas as pd
import glob
import os

# 1. Path to your raw data
path = 'data/raw' 
all_files = glob.glob(os.path.join(path, "tn*.csv"))

li = []

for filename in all_files:
    # 'latin1' encoding prevents the crash you saw in your screenshots
    df = pd.read_csv(filename, index_col=None, header=0, encoding='latin1')
    
    # Create a 'Crime_Type' column based on the filename (e.g., MURDER)
    category = os.path.basename(filename).replace('tn', '').replace('.csv', '').upper()
    df['Crime_Type'] = category
    
    li.append(df)

# 2. Combine all files into one
frame = pd.concat(li, axis=0, ignore_index=True)

# 3. Save the master file
frame.to_csv('data/raw/tamilnadu_master.csv', index=False)
print("✅ Merged successfully! Use 'tamilnadu_master.csv' in your app.")
