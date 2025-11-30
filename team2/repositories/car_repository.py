"""
Car repository for database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_mysql_pool, get_mongo_db
from config.redis_config import CacheManager

class CarRepository:
    """Repository for car data access"""
    
    @staticmethod
    def create(car_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new car listing"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            car_id = f"CAR-{uuid.uuid4().hex[:12].upper()}"
            
            query = """
                INSERT INTO cars (
                    car_id, car_type, company_provider_name, model_and_year,
                    transmission_type, number_of_seats, daily_rental_price,
                    availability_status, location_city, location_state, location_address
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            cursor.execute(query, (
                car_id,
                car_data['car_type'],
                car_data['company_provider_name'],
                car_data['model_and_year'],
                car_data['transmission_type'],
                car_data['number_of_seats'],
                car_data['daily_rental_price'],
                car_data.get('availability_status', 'Available'),
                car_data.get('location_city'),
                car_data.get('location_state'),
                car_data.get('location_address')
            ))
            conn.commit()
            
            return CarRepository.get_by_id(car_id)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(car_id: str) -> Optional[Dict[str, Any]]:
        """Get car by ID with caching"""
        # Check cache first
        cached = CacheManager.get('car', car_id)
        if cached:
            return cached
        
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM cars WHERE car_id = %s"
            cursor.execute(query, (car_id,))
            result = cursor.fetchone()
            
            if result:
                car = dict(result)
                for key in ['created_at', 'updated_at']:
                    if car.get(key) and isinstance(car[key], datetime):
                        car[key] = car[key].isoformat()
                
                # Cache the result
                CacheManager.set('car', car_id, car)
                return car
            return None
        finally:
            conn.close()
    
    @staticmethod
    def update(car_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update car"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            for key, value in update_data.items():
                if value is not None:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return CarRepository.get_by_id(car_id)
            
            values.append(car_id)
            query = f"UPDATE cars SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE car_id = %s"
            cursor.execute(query, values)
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('car', car_id)
            
            return CarRepository.get_by_id(car_id)
        finally:
            conn.close()
    
    @staticmethod
    def delete(car_id: str) -> bool:
        """Delete car"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = "DELETE FROM cars WHERE car_id = %s"
            cursor.execute(query, (car_id,))
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('car', car_id)
            
            # Delete images from MongoDB
            mongo_db = get_mongo_db()
            mongo_db.car_images.delete_many({'car_id': car_id})
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def search(search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search cars with filters"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if search_params.get('location'):
                conditions.append("(location_city LIKE %s OR location_state LIKE %s)")
                location_pattern = f"%{search_params['location']}%"
                params.extend([location_pattern, location_pattern])
            
            if search_params.get('city'):
                conditions.append("location_city = %s")
                params.append(search_params['city'])
            
            if search_params.get('state'):
                conditions.append("location_state = %s")
                params.append(search_params['state'])
            
            if search_params.get('car_type'):
                conditions.append("car_type = %s")
                params.append(search_params['car_type'])
            
            if search_params.get('min_price'):
                conditions.append("daily_rental_price >= %s")
                params.append(search_params['min_price'])
            
            if search_params.get('max_price'):
                conditions.append("daily_rental_price <= %s")
                params.append(search_params['max_price'])
            
            if search_params.get('transmission_type'):
                conditions.append("transmission_type = %s")
                params.append(search_params['transmission_type'])
            
            if search_params.get('min_seats'):
                conditions.append("number_of_seats >= %s")
                params.append(search_params['min_seats'])
            
            if search_params.get('max_seats'):
                conditions.append("number_of_seats <= %s")
                params.append(search_params['max_seats'])
            
            # Availability check
            conditions.append("availability_status = 'Available'")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Count total
            count_query = f"SELECT COUNT(*) as total FROM cars WHERE {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Get paginated results
            page = search_params.get('page', 1)
            page_size = search_params.get('page_size', 20)
            offset = (page - 1) * page_size
            
            query = f"""
                SELECT * FROM cars 
                WHERE {where_clause}
                ORDER BY car_rating DESC, daily_rental_price ASC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cars = []
            for row in results:
                car = dict(row)
                for key in ['created_at', 'updated_at']:
                    if car.get(key) and isinstance(car[key], datetime):
                        car[key] = car[key].isoformat()
                cars.append(car)
            
            return {
                'cars': cars,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        finally:
            conn.close()
    
    @staticmethod
    def update_availability_status(car_id: str, status: str) -> bool:
        """Update car availability status"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE cars 
                SET availability_status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE car_id = %s
            """
            cursor.execute(query, (status, car_id))
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('car', car_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def update_rating(car_id: str, new_rating: float, total_reviews: int) -> bool:
        """Update car rating"""
        conn = get_mysql_pool()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE cars 
                SET car_rating = %s, total_reviews = %s, updated_at = CURRENT_TIMESTAMP
                WHERE car_id = %s
            """
            cursor.execute(query, (new_rating, total_reviews, car_id))
            conn.commit()
            
            # Invalidate cache
            CacheManager.delete('car', car_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def save_image(car_id: str, image_data: bytes, metadata: Dict[str, Any]) -> str:
        """Save car image to MongoDB"""
        mongo_db = get_mongo_db()
        image_doc = {
            'car_id': car_id,
            'image_data': image_data,
            'metadata': metadata,
            'created_at': datetime.utcnow()
        }
        result = mongo_db.car_images.insert_one(image_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_images(car_id: str) -> List[Dict[str, Any]]:
        """Get car images from MongoDB"""
        mongo_db = get_mongo_db()
        images = list(mongo_db.car_images.find({'car_id': car_id}, {'image_data': 1, 'metadata': 1, 'created_at': 1}))
        for img in images:
            img['_id'] = str(img['_id'])
            if img.get('created_at'):
                img['created_at'] = img['created_at'].isoformat()
        return images

