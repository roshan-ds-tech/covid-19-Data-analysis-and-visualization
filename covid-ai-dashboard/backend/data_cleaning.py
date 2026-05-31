import pandas as pd  # pyrefly: ignore [missing-import]
import os

def clean_and_merge_data(base_path):
    print("Loading RAW datasets...")
    confirmed_path = os.path.join(base_path, 'RAW_global_confirmed_cases.csv')
    deaths_path = os.path.join(base_path, 'RAW_global_deaths.csv')
    
    df_confirmed = pd.read_csv(confirmed_path)
    df_deaths = pd.read_csv(deaths_path)
    
    print("Melting DataFrames...")
    id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long']
    
    df_confirmed_melted = df_confirmed.melt(
        id_vars=id_vars, 
        var_name='Date', 
        value_name='Confirmed'
    )
    
    df_deaths_melted = df_deaths.melt(
        id_vars=id_vars, 
        var_name='Date', 
        value_name='Deaths'
    )
    
    print("Merging DataFrames...")
    df_merged = pd.merge(
        df_confirmed_melted, 
        df_deaths_melted, 
        how='left', 
        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date']
    )
    
    print("Cleaning and Formatting...")
    df_merged['Province/State'] = df_merged['Province/State'].fillna('Unknown')
    
    df_merged['Date'] = pd.to_datetime(df_merged['Date'])
    
    df_merged.sort_values(by=['Country/Region', 'Date'], inplace=True)
    df_merged.reset_index(drop=True, inplace=True)
    
    df_merged['Daily_Confirmed'] = df_merged.groupby(['Country/Region', 'Province/State'])['Confirmed'].diff().fillna(0)
    df_merged['Daily_Deaths'] = df_merged.groupby(['Country/Region', 'Province/State'])['Deaths'].diff().fillna(0)
    
    df_merged['Daily_Confirmed'] = df_merged['Daily_Confirmed'].clip(lower=0)
    df_merged['Daily_Deaths'] = df_merged['Daily_Deaths'].clip(lower=0)
    
    print(f"Final shape: {df_merged.shape}")
    
    output_dir = os.path.join(base_path, 'cleaned')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, 'cleaned_covid_data.csv')
    df_merged.to_csv(output_file, index=False)
    print(f"Saved cleaned data to {output_file}")

if __name__ == "__main__":
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets'))
    clean_and_merge_data(dataset_dir)
