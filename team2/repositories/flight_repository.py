"""
Flight repository for database operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from datetime import datetime
import uuid
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_mysql_pool
from config.redis_config import CacheManager
import json

class FlightRepository:
    """Repository for flight data access"""
    
    @staticmethod
    def create(flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new flight"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            flight_id = f"FLT-{uuid.uuid4().hex[:12].upper()}"
            
            query = """
                INSERT INTO flights (
                    flight_id, airline, departure_airport, arrival_airport,
                    departure_date_time, arrival_date_time, duration_minutes,
                    flight_class, ticket_price, total_available_seats,
                    current_available_seats
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            current_seats = flight_data.get('current_available_seats', flight_data.get('total_available_seats', 0))
            
            cursor.execute(query, (
                flight_id,
                flight_data['airline'],
                flight_data['departure_airport'],
                flight_data['arrival_airport'],
                flight_data['departure_date_time'],
                flight_data['arrival_date_time'],
                flight_data['duration_minutes'],
                flight_data['flight_class'],
                flight_data['ticket_price'],
                flight_data['total_available_seats'],
                current_seats
            ))
            conn.commit()
            
            # Get created flight
            flight = FlightRepository.get_by_id(flight_id)
            return flight
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(flight_id: str) -> Optional[Dict[str, Any]]:
        """Get flight by ID with caching"""
        # Check cache first
        cached = CacheManager.get('flight', flight_id)
        if cached:
            return cached
        
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM flights WHERE flight_id = %s"
            cursor.execute(query, (flight_id,))
            result = cursor.fetchone()
            
            if result:
                # Convert datetime objects to strings for JSON serialization
                flight = dict(result)
                for key in ['departure_date_time', 'arrival_date_time', 'created_at', 'updated_at']:
                    if flight.get(key) and isinstance(flight[key], datetime):
                        flight[key] = flight[key].isoformat()
                
                # Cache the result
                CacheManager.set('flight', flight_id, flight)
                return flight
            return None
        finally:
            conn.close()
    
    @staticmethod
    def update(flight_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update flight"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            values = []
            for key, value in update_data.items():
                if value is not None:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return FlightRepository.get_by_id(flight_id)
            
            values.append(flight_id)
            query = f"UPDATE flights SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE flight_id = %s"
            cursor.execute(query, values)
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('flight', flight_id)
            
            return FlightRepository.get_by_id(flight_id)
        finally:
            conn.close()
    
    @staticmethod
    def delete(flight_id: str) -> bool:
        """Delete flight"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = "DELETE FROM flights WHERE flight_id = %s"
            cursor.execute(query, (flight_id,))
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('flight', flight_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def search(search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search flights with filters"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            
            # Build WHERE clause
            conditions = []
            params = []
            
            if search_params.get('origin'):
                conditions.append("departure_airport = %s")
                params.append(search_params['origin'])
            
            if search_params.get('destination'):
                conditions.append("arrival_airport = %s")
                params.append(search_params['destination'])
            
            if search_params.get('departure_date'):
                conditions.append("DATE(departure_date_time) = %s")
                params.append(search_params['departure_date'].date() if isinstance(search_params['departure_date'], datetime) else search_params['departure_date'])
            
            if search_params.get('min_price'):
                conditions.append("ticket_price >= %s")
                params.append(search_params['min_price'])
            
            if search_params.get('max_price'):
                conditions.append("ticket_price <= %s")
                params.append(search_params['max_price'])
            
            if search_params.get('flight_class'):
                conditions.append("flight_class = %s")
                params.append(search_params['flight_class'])
            
            # Time filters
            if search_params.get('departure_time_start'):
                conditions.append("TIME(departure_date_time) >= %s")
                params.append(search_params['departure_time_start'])
            
            if search_params.get('departure_time_end'):
                conditions.append("TIME(departure_date_time) <= %s")
                params.append(search_params['departure_time_end'])
            
            if search_params.get('arrival_time_start'):
                conditions.append("TIME(arrival_date_time) >= %s")
                params.append(search_params['arrival_time_start'])
            
            if search_params.get('arrival_time_end'):
                conditions.append("TIME(arrival_date_time) <= %s")
                params.append(search_params['arrival_time_end'])
            
            # Availability check
            conditions.append("current_available_seats > 0")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Count total
            count_query = f"SELECT COUNT(*) as total FROM flights WHERE {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Get paginated results
            page = search_params.get('page', 1)
            page_size = search_params.get('page_size', 20)
            offset = (page - 1) * page_size
            
            query = f"""
                SELECT * FROM flights 
                WHERE {where_clause}
                ORDER BY ticket_price ASC, departure_date_time ASC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert results
            flights = []
            for row in results:
                flight = dict(row)
                for key in ['departure_date_time', 'arrival_date_time', 'created_at', 'updated_at']:
                    if flight.get(key) and isinstance(flight[key], datetime):
                        flight[key] = flight[key].isoformat()
                flights.append(flight)
            
            return {
                'flights': flights,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        finally:
            conn.close()
    
    @staticmethod
    def update_availability(flight_id: str, seats_change: int) -> bool:
        """Update flight availability"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE flights 
                SET current_available_seats = current_available_seats + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE flight_id = %s AND current_available_seats + %s >= 0
            """
            cursor.execute(query, (seats_change, flight_id, seats_change))
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('flight', flight_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def update_rating(flight_id: str, new_rating: float, total_reviews: int) -> bool:
        """Update flight rating"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE flights 
                SET flight_rating = %s, total_reviews = %s, updated_at = CURRENT_TIMESTAMP
                WHERE flight_id = %s
            """
            cursor.execute(query, (new_rating, total_reviews, flight_id))
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('flight', flight_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()

