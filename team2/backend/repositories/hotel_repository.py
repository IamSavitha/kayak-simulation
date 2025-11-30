"""
Hotel repository for database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.common.database import get_mysql_connection, get_mongo_db
from backend.common.cache import CacheManager

class HotelRepository:
    """Repository for hotel data access"""
    
    @staticmethod
    def create(hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new hotel"""
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            hotel_id = f"HTL-{uuid.uuid4().hex[:12].upper()}"
            
            query = """
                INSERT INTO hotels (
                    hotel_id, hotel_name, address, city, state, zip_code,
                    star_rating, number_of_rooms, current_available_rooms,
                    room_type, price_per_night, amenities, latitude, longitude
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            current_rooms = hotel_data.get('current_available_rooms', hotel_data.get('number_of_rooms', 0))
            
            cursor.execute(query, (
                hotel_id,
                hotel_data['hotel_name'],
                hotel_data['address'],
                hotel_data['city'],
                hotel_data['state'],
                hotel_data['zip_code'],
                hotel_data['star_rating'],
                hotel_data['number_of_rooms'],
                current_rooms,
                hotel_data['room_type'],
                hotel_data['price_per_night'],
                hotel_data.get('amenities'),
                hotel_data.get('latitude'),
                hotel_data.get('longitude')
            ))
            conn.commit()
            
            return HotelRepository.get_by_id(hotel_id)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(hotel_id: str) -> Optional[Dict[str, Any]]:
        """Get hotel by ID with caching"""
        cached = CacheManager.get('hotel', hotel_id)
        if cached:
            return cached
        
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM hotels WHERE hotel_id = %s"
            cursor.execute(query, (hotel_id,))
            result = cursor.fetchone()
            
            if result:
                hotel = dict(result)
                for key in ['created_at', 'updated_at']:
                    if hotel.get(key) and isinstance(hotel[key], datetime):
                        hotel[key] = hotel[key].isoformat()
                
                CacheManager.set('hotel', hotel_id, hotel)
                return hotel
            return None
        finally:
            conn.close()
    
    @staticmethod
    def update(hotel_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update hotel"""
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            for key, value in update_data.items():
                if value is not None:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return HotelRepository.get_by_id(hotel_id)
            
            values.append(hotel_id)
            query = f"UPDATE hotels SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE hotel_id = %s"
            cursor.execute(query, values)
            conn.commit()
            
            CacheManager.delete('hotel', hotel_id)
            
            return HotelRepository.get_by_id(hotel_id)
        finally:
            conn.close()
    
    @staticmethod
    def delete(hotel_id: str) -> bool:
        """Delete hotel"""
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            query = "DELETE FROM hotels WHERE hotel_id = %s"
            cursor.execute(query, (hotel_id,))
            conn.commit()
            
            CacheManager.delete('hotel', hotel_id)
            
            mongo_db = get_mongo_db()
            mongo_db.hotel_images.delete_many({'hotel_id': hotel_id})
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def search(search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search hotels with filters"""
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if search_params.get('location'):
                conditions.append("(city LIKE %s OR state LIKE %s)")
                location_pattern = f"%{search_params['location']}%"
                params.extend([location_pattern, location_pattern])
            
            if search_params.get('city'):
                conditions.append("city = %s")
                params.append(search_params['city'])
            
            if search_params.get('state'):
                conditions.append("state = %s")
                params.append(search_params['state'])
            
            if search_params.get('min_price'):
                conditions.append("price_per_night >= %s")
                params.append(search_params['min_price'])
            
            if search_params.get('max_price'):
                conditions.append("price_per_night <= %s")
                params.append(search_params['max_price'])
            
            if search_params.get('min_stars'):
                conditions.append("star_rating >= %s")
                params.append(search_params['min_stars'])
            
            if search_params.get('max_stars'):
                conditions.append("star_rating <= %s")
                params.append(search_params['max_stars'])
            
            if search_params.get('amenities'):
                for amenity in search_params['amenities']:
                    conditions.append("amenities LIKE %s")
                    params.append(f"%{amenity}%")
            
            conditions.append("current_available_rooms > 0")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            count_query = f"SELECT COUNT(*) as total FROM hotels WHERE {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            page = search_params.get('page', 1)
            page_size = search_params.get('page_size', 20)
            offset = (page - 1) * page_size
            
            query = f"""
                SELECT * FROM hotels 
                WHERE {where_clause}
                ORDER BY hotel_rating DESC, price_per_night ASC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            hotels = []
            for row in results:
                hotel = dict(row)
                for key in ['created_at', 'updated_at']:
                    if hotel.get(key) and isinstance(hotel[key], datetime):
                        hotel[key] = hotel[key].isoformat()
                hotels.append(hotel)
            
            return {
                'hotels': hotels,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        finally:
            conn.close()
    
    @staticmethod
    def update_availability(hotel_id: str, rooms_change: int) -> bool:
        """Update hotel availability"""
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE hotels 
                SET current_available_rooms = current_available_rooms + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE hotel_id = %s AND current_available_rooms + %s >= 0
            """
            cursor.execute(query, (rooms_change, hotel_id, rooms_change))
            conn.commit()
            
            CacheManager.delete('hotel', hotel_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def update_rating(hotel_id: str, new_rating: float, total_reviews: int) -> bool:
        """Update hotel rating"""
        conn = get_mysql_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE hotels 
                SET hotel_rating = %s, total_reviews = %s, updated_at = CURRENT_TIMESTAMP
                WHERE hotel_id = %s
            """
            cursor.execute(query, (new_rating, total_reviews, hotel_id))
            conn.commit()
            
            CacheManager.delete('hotel', hotel_id)
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def save_image(hotel_id: str, image_type: str, image_data: bytes, metadata: Dict[str, Any]) -> str:
        """Save hotel image to MongoDB"""
        mongo_db = get_mongo_db()
        image_doc = {
            'hotel_id': hotel_id,
            'image_type': image_type,
            'image_data': image_data,
            'metadata': metadata,
            'created_at': datetime.utcnow()
        }
        result = mongo_db.hotel_images.insert_one(image_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_images(hotel_id: str, image_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get hotel images from MongoDB"""
        mongo_db = get_mongo_db()
        query = {'hotel_id': hotel_id}
        if image_type:
            query['image_type'] = image_type
        
        images = list(mongo_db.hotel_images.find(query, {'image_data': 0}))
        for img in images:
            img['_id'] = str(img['_id'])
            if img.get('created_at'):
                img['created_at'] = img['created_at'].isoformat()
        return images

