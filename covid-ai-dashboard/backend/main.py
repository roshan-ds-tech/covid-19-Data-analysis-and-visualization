from fastapi import FastAPI, HTTPException, Body  # pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware  # pyrefly: ignore [missing-import]
import pandas as pd  # pyrefly: ignore [missing-import]
import os
from sklearn.linear_model import LinearRegression  # pyrefly: ignore [missing-import]
import numpy as np  # pyrefly: ignore [missing-import]
from datetime import timedelta
from pydantic import BaseModel  # pyrefly: ignore [missing-import]
from typing import List, Optional

app = FastAPI(title="COVID-19 AI Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'cleaned', 'cleaned_covid_data.csv')
df = None
daily_global = None

@app.on_event("startup")
def load_data():
    global df
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df['Date'] = pd.to_datetime(df['Date'])
        global daily_global
        daily_global = df.groupby('Date')[['Confirmed', 'Deaths']].sum().reset_index()
    else:
        print(f"Warning: Cleaned dataset not found at {DATA_PATH}")

@app.get("/")
def read_root():
    return {"message": "Welcome to COVID-19 AI Analytics API"}

@app.get("/api/countries")
def get_countries():
    if df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    return {"countries": sorted(df['Country/Region'].unique().tolist())}

@app.get("/api/dates")
def get_dates():
    if df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    return {
        "min_date": df['Date'].min().strftime('%Y-%m-%d'),
        "max_date": df['Date'].max().strftime('%Y-%m-%d')
    }

class DashboardRequest(BaseModel):
    countries: List[str]
    start_date: str
    end_date: str

@app.post("/api/dashboard")
def get_dashboard_data(req: DashboardRequest):
    if df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    # 1. Filter Data
    filtered = df[(df['Date'] >= req.start_date) & (df['Date'] <= req.end_date)]
    if req.countries:
        filtered = filtered[filtered['Country/Region'].isin(req.countries)]

    if filtered.empty:
        return {"error": "No data found for the selected filters."}

    latest_date = filtered['Date'].max()
    latest_filtered = filtered[filtered['Date'] == latest_date]

    # Global mapping (for choropleth map, usually shows all countries at the latest date)
    global_latest = df[df['Date'] == df['Date'].max()]
    map_data = global_latest.groupby('Country/Region', as_index=False)[['Confirmed', 'Deaths']].sum()

    # KPIs
    f_total_cases = int(latest_filtered['Confirmed'].sum())
    f_total_deaths = int(latest_filtered['Deaths'].sum())

    # Daily Trend (Line Chart)
    daily_trend = filtered.groupby(['Date', 'Country/Region'])['Daily_Confirmed'].sum().reset_index()
    trend_data = {}
    for country in daily_trend['Country/Region'].unique():
        country_df = daily_trend[daily_trend['Country/Region'] == country]
        trend_data[country] = {
            "dates": country_df['Date'].dt.strftime('%Y-%m-%d').tolist(),
            "cases": country_df['Daily_Confirmed'].tolist()
        }

    # Top Affected (Bar Chart)
    top_affected = latest_filtered.groupby('Country/Region')['Confirmed'].sum().reset_index().sort_values('Confirmed', ascending=False)
    
    # Heatmap (Correlation)
    country_pivot = daily_trend.pivot(index='Date', columns='Country/Region', values='Daily_Confirmed').fillna(0)
    corr_matrix = country_pivot.corr()
    
    # ML Prediction (for the first selected country)
    prediction = None
    if req.countries and len(req.countries) > 0:
        target_country = req.countries[0]
        country_data = daily_trend[daily_trend['Country/Region'] == target_country].copy()
        if not country_data.empty and len(country_data) > 10:
            country_data['Days'] = (country_data['Date'] - country_data['Date'].min()).dt.days
            X = country_data[['Days']].values
            y = country_data['Daily_Confirmed'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            last_day = country_data['Days'].max()
            last_date = country_data['Date'].max()
            
            future_days = np.array([[last_day + i] for i in range(1, 31)])
            future_preds = model.predict(future_days)
            future_dates = [(last_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 31)]
            
            prediction = {
                "country": target_country,
                "future_dates": future_dates,
                "predicted_cases": [max(0, int(p)) for p in future_preds],
                "hist_dates": country_data['Date'].dt.strftime('%Y-%m-%d').tolist(),
                "hist_trend": [max(0, int(p)) for p in model.predict(X)]
            }

    return {
        "kpi": {
            "total_cases": f_total_cases,
            "total_deaths": f_total_deaths,
            "latest_date": latest_date.strftime('%Y-%m-%d')
        },
        "trends": trend_data,
        "top_affected": {
            "countries": top_affected['Country/Region'].tolist(),
            "cases": top_affected['Confirmed'].tolist()
        },
        "scatter": {
            "countries": latest_filtered['Country/Region'].tolist(),
            "cases": latest_filtered['Confirmed'].tolist(),
            "deaths": latest_filtered['Deaths'].tolist()
        },
        "map": {
            "countries": map_data['Country/Region'].tolist(),
            "cases": map_data['Confirmed'].tolist()
        },
        "heatmap": {
            "x": corr_matrix.columns.tolist(),
            "y": corr_matrix.index.tolist(),
            "z": corr_matrix.values.tolist()
        },
        "prediction": prediction
    }
