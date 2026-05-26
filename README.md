# COVID-19 Data Analysis and Visualization Dashboard

An enterprise-grade, full-stack dashboard for analyzing and visualizing COVID-19 data. This project includes a robust Next.js frontend, a FastAPI backend for data processing and machine learning predictions, and a rapid-prototyping Streamlit application.

## 🚀 Features
- **Next.js 13+ App Router Frontend:** Built with React 18, Tailwind CSS, and Plotly.js for interactive and responsive charting.
- **FastAPI Backend:** High-performance Python backend serving clean data, metrics, and machine learning predictions.
- **Machine Learning Integration:** Uses `scikit-learn` Linear Regression to predict future COVID-19 cases based on historical trends.
- **Interactive Visualizations:** Includes daily trend line charts, top affected country bar charts, a global choropleth map, correlation heatmaps, and scatter plots.
- **Streamlit Prototype:** A secondary, pure-Python dashboard for Data Science exploratory data analysis (EDA).

---

## 🛠️ Project Structure
```text
covid-19_DAV/
│
├── covid-ai-dashboard/
│   ├── backend/               # FastAPI Server, Data Cleaning, and ML Models
│   ├── frontend/              # Next.js React Dashboard
│   ├── datasets/              # Cleaned CSV Datasets used by the backend
│   └── streamlit_app.py       # Standalone Streamlit Prototyping App
│
├── archive/                   # Raw, unprocessed datasets
├── README.md                  # Project Documentation
└── .gitignore                 # Git ignore file
```

---

## 💻 Setup Instructions

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**

### 1. Backend Setup (FastAPI)
The backend is responsible for loading the dataset, running the machine learning model, and providing the API for the frontend.

```bash
# Navigate to the backend directory
cd covid-ai-dashboard/backend

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the data cleaning script (if the dataset is not yet cleaned)
python data_cleaning.py

# Start the FastAPI server
uvicorn main:app --reload
```
*The backend API will run locally at: `http://127.0.0.1:8000`*

### 2. Frontend Setup (Next.js)
The frontend is the primary user interface.

```bash
# Open a new terminal and navigate to the frontend directory
cd covid-ai-dashboard/frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```
*The frontend dashboard will run locally at: `http://localhost:3000`*

### 3. Streamlit App (Optional EDA Prototype)
If you want to view the pure Python data science prototype:

```bash
# Open a new terminal and navigate to the dashboard root
cd covid-ai-dashboard

# Run the Streamlit app
streamlit run streamlit_app.py
```
*The Streamlit app will run locally at: `http://localhost:8501`*

---

## 🧠 Machine Learning Details
The backend utilizes a Scikit-Learn `LinearRegression` model. When the frontend requests a prediction for a specific country, the backend trains a regression model on the fly using that country's historical daily confirmed cases, and predicts the trajectory for the next 30 days.

## 🎨 UI/UX Design
The Next.js frontend was designed with modern enterprise aesthetics in mind, featuring:
- Glassmorphism effects
- Clean, minimal Tailwind styling
- Responsive grid layouts
- Custom Plotly layouts that adapt to window resizing.

## 🤝 Contributing
Feel free to open issues or submit pull requests with improvements.
