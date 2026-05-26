import pandas as pd  # pyrefly: ignore [missing-import]
import os

def clean_and_merge_data(base_path):
    print("Loading RAW datasets...")
    # Paths
    confirmed_path = os.path.join(base_path, 'RAW_global_confirmed_cases.csv')
    deaths_path = os.path.join(base_path, 'RAW_global_deaths.csv')
    
    # Read Data
    df_confirmed = pd.read_csv(confirmed_path)
    df_deaths = pd.read_csv(deaths_path)
    
    print("Melting DataFrames...")
    # Melt DataFrames (Convert wide format to long format)
    # The first 4 columns are: Province/State, Country/Region, Lat, Long
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
    # Merge confirmed and deaths
    df_merged = pd.merge(
        df_confirmed_melted, 
        df_deaths_melted, 
        how='left', 
        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date']
    )
    
    print("Cleaning and Formatting...")
    # Handle missing values
    df_merged['Province/State'] = df_merged['Province/State'].fillna('Unknown')
    
    # Convert Date column to datetime
    df_merged['Date'] = pd.to_datetime(df_merged['Date'])
    
    # Remove rows where Confirmed and Deaths are both 0 early on (optional optimization)
    # df_merged = df_merged[(df_merged['Confirmed'] > 0) | (df_merged['Deaths'] > 0)]
    
    # Sort by country and date
    df_merged.sort_values(by=['Country/Region', 'Date'], inplace=True)
    df_merged.reset_index(drop=True, inplace=True)
    
    # Calculate daily new cases and deaths
    df_merged['Daily_Confirmed'] = df_merged.groupby(['Country/Region', 'Province/State'])['Confirmed'].diff().fillna(0)
    df_merged['Daily_Deaths'] = df_merged.groupby(['Country/Region', 'Province/State'])['Deaths'].diff().fillna(0)
    
    # Ensure no negative daily cases/deaths due to data corrections
    df_merged['Daily_Confirmed'] = df_merged['Daily_Confirmed'].clip(lower=0)
    df_merged['Daily_Deaths'] = df_merged['Daily_Deaths'].clip(lower=0)
    
    print(f"Final shape: {df_merged.shape}")
    
    # Save the cleaned data
    output_dir = os.path.join(base_path, 'cleaned')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, 'cleaned_covid_data.csv')
    df_merged.to_csv(output_file, index=False)
    print(f"Saved cleaned data to {output_file}")

if __name__ == "__main__":
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets'))
    clean_and_merge_data(dataset_dir)
