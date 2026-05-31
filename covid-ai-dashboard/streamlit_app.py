import streamlit as st  # pyrefly: ignore [missing-import]
import pandas as pd  # pyrefly: ignore [missing-import]
import plotly.express as px  # pyrefly: ignore [missing-import]
import plotly.graph_objects as go  # pyrefly: ignore [missing-import]
import numpy as np  # pyrefly: ignore [missing-import]
from sklearn.linear_model import LinearRegression  # pyrefly: ignore [missing-import]
from datetime import timedelta
import os

st.set_page_config(
    page_title="COVID-19 AI Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    data_path = os.path.join(base_path, 'datasets', 'cleaned', 'cleaned_covid_data.csv')
    
    if not os.path.exists(data_path):
        return None
        
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

st.title("COVID-19 AI Analytics Dashboard (Prototype)")

with st.spinner("Loading Data..."):
    df = load_data()

if df is None:
    st.error("Data not found! Please run backend/data_cleaning.py first.")
    st.stop()

st.sidebar.header("Filters")
all_countries = df['Country/Region'].unique()
selected_countries = st.sidebar.multiselect(
    "Select Countries", 
    options=all_countries,
    default=['US', 'India', 'Brazil', 'United Kingdom', 'France']
)

min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if selected_countries:
    filtered_df = df[df['Country/Region'].isin(selected_countries)]
else:
    filtered_df = df

filtered_df = filtered_df[(filtered_df['Date'].dt.date >= start_date) & (filtered_df['Date'].dt.date <= end_date)]

latest_global = df[df['Date'] == df['Date'].max()]
total_cases = latest_global['Confirmed'].sum()
total_deaths = latest_global['Deaths'].sum()

latest_filtered = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
f_total_cases = latest_filtered['Confirmed'].sum()
f_total_deaths = latest_filtered['Deaths'].sum()

st.markdown("### Global Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Global Total Cases", f"{total_cases:,.0f}")
col2.metric("Global Total Deaths", f"{total_deaths:,.0f}")
col3.metric("Filtered Total Cases", f"{f_total_cases:,.0f}")
col4.metric("Filtered Total Deaths", f"{f_total_deaths:,.0f}")

st.markdown("---")

st.subheader("Daily Cases Trend")
daily_trend = filtered_df.groupby(['Date', 'Country/Region'])['Daily_Confirmed'].sum().reset_index()
fig_line = px.line(daily_trend, x='Date', y='Daily_Confirmed', color='Country/Region', title='Daily Confirmed Cases')
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Top Affected Countries (Filtered)")
top_countries = latest_filtered.groupby('Country/Region')['Confirmed'].sum().reset_index().sort_values('Confirmed', ascending=False)
fig_bar = px.bar(top_countries, x='Country/Region', y='Confirmed', color='Country/Region', title='Total Confirmed Cases by Country')
st.plotly_chart(fig_bar, use_container_width=True)

col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.subheader("Cases vs Deaths (Latest)")
    pie_data = pd.DataFrame({
        'Status': ['Total Cases', 'Total Deaths'],
        'Count': [f_total_cases, f_total_deaths]
    })
    fig_pie = px.pie(pie_data, names='Status', values='Count', title='Cases vs Deaths')
    st.plotly_chart(fig_pie, use_container_width=True)

with col_viz2:
    st.subheader("Cases vs Deaths by Region")
    fig_scatter = px.scatter(latest_filtered, x='Confirmed', y='Deaths', color='Country/Region', hover_name='Province/State', title='Correlation: Confirmed vs Deaths')
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Global Spread (Choropleth Map)")
world_data = latest_global.groupby('Country/Region', as_index=False).agg({'Confirmed': 'sum', 'Deaths': 'sum'})
fig_map = px.choropleth(
    world_data,
    locations="Country/Region",
    locationmode='country names',
    color="Confirmed",
    hover_name="Country/Region",
    color_continuous_scale=px.colors.sequential.Plasma,
    title="Global COVID-19 Confirmed Cases"
)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Correlation Heatmap")
country_pivot = daily_trend.pivot(index='Date', columns='Country/Region', values='Daily_Confirmed').fillna(0)
corr_matrix = country_pivot.corr()
fig_heatmap = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation of Daily Cases between Countries")
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")
st.header("AI/ML Forecast (Next 30 Days)")
st.write("Using Linear Regression to predict future confirmed cases based on historical data.")

if len(selected_countries) > 0:
    target_country = selected_countries[0]
    st.subheader(f"Prediction for: {target_country}")
    
    country_data = daily_trend[daily_trend['Country/Region'] == target_country].copy()
    country_data['Days'] = (country_data['Date'] - country_data['Date'].min()).dt.days
    
    if not country_data.empty and len(country_data) > 10:
        X = country_data[['Days']].values
        y = country_data['Daily_Confirmed'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        country_data['Predicted'] = model.predict(X)
        
        last_day = country_data['Days'].max()
        future_days = np.array([[last_day + i] for i in range(1, 31)])
        future_preds = model.predict(future_days)
        
        future_dates = [country_data['Date'].max() + timedelta(days=i) for i in range(1, 31)]
        future_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted_New_Cases': future_preds
        })
        
        future_df['Predicted_New_Cases'] = future_df['Predicted_New_Cases'].clip(lower=0)
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=country_data['Date'], y=country_data['Daily_Confirmed'], mode='lines', name='Actual Cases'))
        fig_pred.add_trace(go.Scatter(x=country_data['Date'], y=country_data['Predicted'], mode='lines', name='Trend Line (LR)', line=dict(dash='dash')))
        fig_pred.add_trace(go.Scatter(x=future_df['Date'], y=future_df['Predicted_New_Cases'], mode='lines', name='Future 30-Day Forecast', line=dict(color='red')))
        
        fig_pred.update_layout(title=f"30-Day Forecast for {target_country} (Linear Regression)", xaxis_title="Date", yaxis_title="Daily Confirmed Cases")
        st.plotly_chart(fig_pred, use_container_width=True)
        
        st.info("The prediction module uses Scikit-learn's Linear Regression on historical daily cases. More complex models (like Random Forest or Time Series) can be selected in the final dashboard.")
    else:
        st.warning("Not enough data to train the model for this country.")
else:
    st.warning("Please select at least one country in the sidebar to view predictions.")

st.success("Prototype Dashboard Loaded Successfully. Note: Streamlit limits animations to standard Plotly features.")
