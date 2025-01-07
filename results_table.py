import pandas as pd
import os 


final_dir = '/Users/mokshahuja/desktop/test_simple'
os.chdir(final_dir)
for file in os.listdir():
    if file.endswith('rates.csv'):
        df_matches = pd.read_csv(file)
        print(df_matches)