import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression

def clean_data(input_path, output_path):
    # Load dataset
    df = pd.read_csv(input_path)
    
    # Check dataset info
    print("Original Dataset Shape:", df.shape)
    
    # 1. Drop irrelevant columns: image_url, video_url
    cols_to_drop = ['image_url', 'video_url', 'production_code']
    df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)
    
    # 2. Date parsing
    df['original_air_date'] = pd.to_datetime(df['original_air_date'], errors='coerce')
    
    # Extract weekday and other date components
    # Monday=0, Sunday=6
    df['weekday_num'] = df['original_air_date'].dt.weekday
    # Full weekday name
    df['weekday_name'] = df['original_air_date'].dt.day_name()
    
    df['year'] = df['original_air_date'].dt.year
    df['month'] = df['original_air_date'].dt.month

    # 4. Standardize types
    df['season'] = df['season'].astype(int)
    df['number_in_season'] = df['number_in_season'].astype(int)
    df['number_in_series'] = df['number_in_series'].astype(int)


    
    # 3. Handle missing values

    # 3.1 Remove season 28 because critical data are missing because not collected yet
    df = df[df['season'] != 28]

    # 3.2 Impute missing values - us_viewers_in_millions in season 8

    # 1. Prepare training data for Season 8
    df_s8_train = df[df['season'] == 8].dropna(subset=['number_in_season', 'us_viewers_in_millions'])

    # X is the feature we HAVE ('views'), y is the target we WANT ('us_viewers_in_millions')
    X_s8 = df_s8_train[['number_in_season']]
    y_s8 = df_s8_train['us_viewers_in_millions']

    # 2. Train Season 8 model
    model_s8 = LinearRegression()
    model_s8.fit(X_s8, y_s8)

    # Impute Season 8 missing data
    s8_missing_mask = (df['season'] == 8) & df['us_viewers_in_millions'].isnull()
    if s8_missing_mask.any():
        df.loc[s8_missing_mask, 'us_viewers_in_millions'] = model_s8.predict(df.loc[s8_missing_mask, ['number_in_season']])
    

    # function to calculate the slope for a group of episodes
    def calculate_slope(group):
        return np.polyfit(group['number_in_season'], group['us_viewers_in_millions'], 1)[0]

    # Apply it to each season and merge it
    trend_data = df.groupby('season').apply(calculate_slope).reset_index(name='trend_slope')
    df = pd.merge(df, trend_data, on='season', how='left')

    # Create viewers_type column
    df['viewers_type'] = df['season'].apply(lambda x: 'Household Viewers (Millions)' if x <= 11 else 'Individual Viewers (Millions)')
    
    # Save the cleaned dataset
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to {output_path}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, "simpsons_episodes.csv")
    output_csv = os.path.join(script_dir, "simpsons_episodes_clean.csv")
    
    clean_data(input_csv, output_csv)
