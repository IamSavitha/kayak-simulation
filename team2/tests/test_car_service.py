"""
Unit tests for Car Service
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def sample_car_data():
    """Sample car data for testing"""
    return {
        'car_type': 'SUV',
        'company_provider_name': 'Hertz',
        'model_and_year': 'Toyota RAV4 2023',
        'transmission_type': 'Automatic',
        'number_of_seats': 5,
        'daily_rental_price': 89.99,
        'availability_status': 'Available',
        'location_city': 'New York',
        'location_state': 'NY'
    }

def test_create_car(sample_car_data):
    """Test creating a car"""
    response = client.post("/cars", json=sample_car_data)
    assert response.status_code == 201
    data = response.json()
    assert data['car_type'] == sample_car_data['car_type']
    assert 'car_id' in data

def test_get_car(sample_car_data):
    """Test getting a car by ID"""
    create_response = client.post("/cars", json=sample_car_data)
    car_id = create_response.json()['car_id']
    
    response = client.get(f"/cars/{car_id}")
    assert response.status_code == 200
    assert response.json()['car_id'] == car_id

def test_search_cars():
    """Test searching cars"""
    response = client.get("/cars/search?city=New York&page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert 'cars' in data
    assert 'total' in data

def test_update_car(sample_car_data):
    """Test updating a car"""
    create_response = client.post("/cars", json=sample_car_data)
    car_id = create_response.json()['car_id']
    
    update_data = {'daily_rental_price': 99.99}
    response = client.put(f"/cars/{car_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()['daily_rental_price'] == 99.99

def test_delete_car(sample_car_data):
    """Test deleting a car"""
    create_response = client.post("/cars", json=sample_car_data)
    car_id = create_response.json()['car_id']
    
    response = client.delete(f"/cars/{car_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/cars/{car_id}")
    assert get_response.status_code == 404

