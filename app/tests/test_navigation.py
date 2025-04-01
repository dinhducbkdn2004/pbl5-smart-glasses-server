import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.route_model import LocationPoint

client = TestClient(app)

def test_get_navigation():
    # Test data
    test_data = {
        "current_location": {
            "latitude": 10.762622,
            "longitude": 106.660172
        },
        "destination": {
            "latitude": 10.762622,
            "longitude": 106.660172
        }
    }
    
    response = client.post("/api/v1/navigation", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "total_distance" in data
    assert "estimated_time" in data
    assert "steps" in data

def test_get_navigation_by_text():
    # Test data
    test_data = {
        "current_location": {
            "latitude": 10.762622,
            "longitude": 106.660172
        },
        "destination_text": "Ben Thanh Market, Ho Chi Minh City"
    }
    
    response = client.post("/api/v1/navigation/by-text", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "total_distance" in data
    assert "estimated_time" in data
    assert "steps" in data

def test_invalid_coordinates():
    # Test with invalid coordinates
    test_data = {
        "current_location": {
            "latitude": 91,  # Invalid latitude
            "longitude": 181  # Invalid longitude
        },
        "destination": {
            "latitude": 10.762622,
            "longitude": 106.660172
        }
    }
    
    response = client.post("/api/v1/navigation", json=test_data)
    assert response.status_code == 422  # Validation error 