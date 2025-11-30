"""
Unit tests for Flight Service
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from repositories.flight_repository import FlightRepository
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture
def sample_flight_data():
    """Sample flight data for testing"""
    return {
        'airline': 'Test Airlines',
        'departure_airport': 'JFK',
        'arrival_airport': 'LAX',
        'departure_date_time': datetime.now() + timedelta(days=30),
        'arrival_date_time': datetime.now() + timedelta(days=30, hours=6),
        'duration_minutes': 360,
        'flight_class': 'Economy',
        'ticket_price': 299.99,
        'total_available_seats': 150,
        'current_available_seats': 150
    }

def test_create_flight(sample_flight_data):
    """Test creating a flight"""
    response = client.post("/flights", json={
        **sample_flight_data,
        'departure_date_time': sample_flight_data['departure_date_time'].isoformat(),
        'arrival_date_time': sample_flight_data['arrival_date_time'].isoformat()
    })
    assert response.status_code == 201
    data = response.json()
    assert data['airline'] == sample_flight_data['airline']
    assert 'flight_id' in data

def test_get_flight(sample_flight_data):
    """Test getting a flight by ID"""
    # First create a flight
    create_response = client.post("/flights", json={
        **sample_flight_data,
        'departure_date_time': sample_flight_data['departure_date_time'].isoformat(),
        'arrival_date_time': sample_flight_data['arrival_date_time'].isoformat()
    })
    flight_id = create_response.json()['flight_id']
    
    # Then get it
    response = client.get(f"/flights/{flight_id}")
    assert response.status_code == 200
    assert response.json()['flight_id'] == flight_id

def test_search_flights():
    """Test searching flights"""
    response = client.get("/flights/search?origin=JFK&destination=LAX&page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert 'flights' in data
    assert 'total' in data
    assert 'page' in data

def test_update_flight(sample_flight_data):
    """Test updating a flight"""
    # Create flight
    create_response = client.post("/flights", json={
        **sample_flight_data,
        'departure_date_time': sample_flight_data['departure_date_time'].isoformat(),
        'arrival_date_time': sample_flight_data['arrival_date_time'].isoformat()
    })
    flight_id = create_response.json()['flight_id']
    
    # Update flight
    update_data = {'ticket_price': 349.99}
    response = client.put(f"/flights/{flight_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()['ticket_price'] == 349.99

def test_delete_flight(sample_flight_data):
    """Test deleting a flight"""
    # Create flight
    create_response = client.post("/flights", json={
        **sample_flight_data,
        'departure_date_time': sample_flight_data['departure_date_time'].isoformat(),
        'arrival_date_time': sample_flight_data['arrival_date_time'].isoformat()
    })
    flight_id = create_response.json()['flight_id']
    
    # Delete flight
    response = client.delete(f"/flights/{flight_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/flights/{flight_id}")
    assert get_response.status_code == 404

def test_update_availability(sample_flight_data):
    """Test updating flight availability"""
    # Create flight
    create_response = client.post("/flights", json={
        **sample_flight_data,
        'departure_date_time': sample_flight_data['departure_date_time'].isoformat(),
        'arrival_date_time': sample_flight_data['arrival_date_time'].isoformat()
    })
    flight_id = create_response.json()['flight_id']
    
    # Update availability
    response = client.put(f"/flights/{flight_id}/availability?seats_change=-5")
    assert response.status_code == 200

