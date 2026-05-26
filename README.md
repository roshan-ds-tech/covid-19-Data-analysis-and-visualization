# COVID-19 Data Analysis Dashboard

A full-stack dashboard for analyzing and visualizing COVID-19 data.

## Project Structure
- `covid-ai-dashboard/backend/`: FastAPI server for data processing and ML predictions.
- `covid-ai-dashboard/frontend/`: Next.js React frontend.
- `covid-ai-dashboard/streamlit_app.py`: Streamlit prototyping app.
- `archive/`: Raw datasets.

## Setup Instructions

### 1. Backend (FastAPI)
```bash
cd covid-ai-dashboard/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python data_cleaning.py
uvicorn main:app --reload
```
Runs on `http://127.0.0.1:8000`

### 2. Frontend (Next.js)
```bash
cd covid-ai-dashboard/frontend
npm install
npm run dev
```
Runs on `http://localhost:3000`

### 3. Streamlit Prototype
```bash
cd covid-ai-dashboard
streamlit run streamlit_app.py
```
Runs on `http://localhost:8501`
