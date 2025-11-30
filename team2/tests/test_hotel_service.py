"""
Unit tests for Hotel Service
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def sample_hotel_data():
    """Sample hotel data for testing"""
    return {
        'hotel_name': 'Test Hotel',
        'address': '123 Test Street',
        'city': 'New York',
        'state': 'NY',
        'zip_code': '10001',
        'star_rating': 4,
        'number_of_rooms': 100,
        'current_available_rooms': 50,
        'room_type': 'Deluxe',
        'price_per_night': 199.99,
        'amenities': 'Wi-Fi, Breakfast, Parking'
    }

def test_create_hotel(sample_hotel_data):
    """Test creating a hotel"""
    response = client.post("/hotels", json=sample_hotel_data)
    assert response.status_code == 201
    data = response.json()
    assert data['hotel_name'] == sample_hotel_data['hotel_name']
    assert 'hotel_id' in data

def test_get_hotel(sample_hotel_data):
    """Test getting a hotel by ID"""
    create_response = client.post("/hotels", json=sample_hotel_data)
    hotel_id = create_response.json()['hotel_id']
    
    response = client.get(f"/hotels/{hotel_id}")
    assert response.status_code == 200
    assert response.json()['hotel_id'] == hotel_id

def test_search_hotels():
    """Test searching hotels"""
    response = client.get("/hotels/search?city=New York&page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert 'hotels' in data
    assert 'total' in data

def test_update_hotel(sample_hotel_data):
    """Test updating a hotel"""
    create_response = client.post("/hotels", json=sample_hotel_data)
    hotel_id = create_response.json()['hotel_id']
    
    update_data = {'price_per_night': 249.99}
    response = client.put(f"/hotels/{hotel_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()['price_per_night'] == 249.99

def test_delete_hotel(sample_hotel_data):
    """Test deleting a hotel"""
    create_response = client.post("/hotels", json=sample_hotel_data)
    hotel_id = create_response.json()['hotel_id']
    
    response = client.delete(f"/hotels/{hotel_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/hotels/{hotel_id}")
    assert get_response.status_code == 404

