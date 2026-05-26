from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_kpi():
    response = client.get("/api/kpi")
    print("KPI Status:", response.status_code)
    print("KPI Data:", response.json())

def test_trends():
    response = client.get("/api/trends?country=US")
    print("Trends Status:", response.status_code)
    
def test_predict():
    response = client.get("/api/predict?country=US")
    print("Predict Status:", response.status_code)

if __name__ == "__main__":
    test_kpi()
    test_trends()
    test_predict()
    print("All tests passed!")
