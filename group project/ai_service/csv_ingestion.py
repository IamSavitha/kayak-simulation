"""
CSV Feed Ingestion Module

Parses CSV files from Kaggle datasets and converts them to normalized listings.
Supports:
- Flight Price Prediction dataset (Clean_Dataset.csv)
- Inside Airbnb listings (listings.csv)
- Hotel Booking dataset (hotel_booking.csv)
"""

import csv
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Generator
from pathlib import Path
from io import StringIO
import random
import re

from pydantic import BaseModel

from .models import NormalizedListing, ListingType

logger = logging.getLogger(__name__)


# ========================================
# CSV Column Mappings (Actual Kaggle Data)
# ========================================

class FlightCSVMapping:
    """Mapping for Clean_Dataset.csv (Flight Price Prediction)
    
    Columns: ,airline,flight,source_city,departure_time,stops,arrival_time,destination_city,class,duration,days_left,price
    """
    AIRLINE = 'airline'
    FLIGHT = 'flight'
    SOURCE_CITY = 'source_city'
    DEPARTURE_TIME = 'departure_time'  # Early_Morning, Morning, Afternoon, Evening, Night
    STOPS = 'stops'  # zero, one, two_or_more
    ARRIVAL_TIME = 'arrival_time'
    DESTINATION_CITY = 'destination_city'
    CLASS = 'class'  # Economy, Business
    DURATION = 'duration'  # float in hours
    DAYS_LEFT = 'days_left'  # days until departure
    PRICE = 'price'  # in INR


class AirbnbCSVMapping:
    """Mapping for listings.csv (Inside Airbnb)
    
    Columns: id,name,host_id,host_name,neighbourhood_group,neighbourhood,latitude,longitude,
             room_type,price,minimum_nights,number_of_reviews,last_review,reviews_per_month,
             calculated_host_listings_count,availability_365,number_of_reviews_ltm,license
    """
    ID = 'id'
    NAME = 'name'
    HOST_ID = 'host_id'
    HOST_NAME = 'host_name'
    NEIGHBOURHOOD_GROUP = 'neighbourhood_group'
    NEIGHBOURHOOD = 'neighbourhood'
    LATITUDE = 'latitude'
    LONGITUDE = 'longitude'
    ROOM_TYPE = 'room_type'  # Entire home/apt, Private room, Shared room
    PRICE = 'price'
    MINIMUM_NIGHTS = 'minimum_nights'
    NUMBER_OF_REVIEWS = 'number_of_reviews'
    LAST_REVIEW = 'last_review'
    REVIEWS_PER_MONTH = 'reviews_per_month'
    AVAILABILITY_365 = 'availability_365'


class HotelBookingCSVMapping:
    """Mapping for hotel_booking.csv
    
    Columns: hotel,is_canceled,lead_time,arrival_date_year,arrival_date_month,arrival_date_week_number,
             arrival_date_day_of_month,stays_in_weekend_nights,stays_in_week_nights,adults,children,babies,
             meal,country,market_segment,distribution_channel,is_repeated_guest,previous_cancellations,
             previous_bookings_not_canceled,reserved_room_type,assigned_room_type,booking_changes,
             deposit_type,agent,company,days_in_waiting_list,customer_type,adr,required_car_parking_spaces,
             total_of_special_requests,reservation_status,reservation_status_date,name,email,phone-number,credit_card
    """
    HOTEL = 'hotel'  # Resort Hotel, City Hotel
    IS_CANCELED = 'is_canceled'
    LEAD_TIME = 'lead_time'
    ARRIVAL_DATE_YEAR = 'arrival_date_year'
    ARRIVAL_DATE_MONTH = 'arrival_date_month'
    ARRIVAL_DATE_DAY = 'arrival_date_day_of_month'
    STAYS_WEEKEND = 'stays_in_weekend_nights'
    STAYS_WEEK = 'stays_in_week_nights'
    ADULTS = 'adults'
    CHILDREN = 'children'
    MEAL = 'meal'  # BB (Bed & Breakfast), FB (Full Board), HB (Half Board), SC (Self Catering)
    COUNTRY = 'country'
    RESERVED_ROOM_TYPE = 'reserved_room_type'
    ASSIGNED_ROOM_TYPE = 'assigned_room_type'
    ADR = 'adr'  # Average Daily Rate
    DEPOSIT_TYPE = 'deposit_type'  # No Deposit, Refundable, Non Refund
    CUSTOMER_TYPE = 'customer_type'
    RESERVATION_STATUS = 'reservation_status'


# ========================================
# CSV Parsers
# ========================================

class FlightCSVParser:
    """Parser for Flight Price Prediction CSV"""
    
    # INR to USD conversion rate (approximate)
    INR_TO_USD = 0.012
    
    # Map stops text to integer
    STOPS_MAP = {
        'zero': 0,
        'one': 1,
        'two_or_more': 2
    }
    
    # Map time periods to approximate hours
    TIME_MAP = {
        'Early_Morning': '05:00',
        'Morning': '08:00',
        'Afternoon': '13:00',
        'Evening': '18:00',
        'Night': '21:00',
        'Late_Night': '23:00'
    }
    
    @classmethod
    def parse_row(cls, row: Dict[str, Any], row_index: int = 0) -> Optional[NormalizedListing]:
        """Parse a single CSV row to NormalizedListing"""
        try:
            # Extract and clean data
            airline = row.get(FlightCSVMapping.AIRLINE, '').strip()
            flight = row.get(FlightCSVMapping.FLIGHT, '').strip()
            source = row.get(FlightCSVMapping.SOURCE_CITY, '').strip()
            destination = row.get(FlightCSVMapping.DESTINATION_CITY, '').strip()
            stops_str = row.get(FlightCSVMapping.STOPS, 'zero').strip().lower()
            fare_class = row.get(FlightCSVMapping.CLASS, 'Economy').strip()
            duration = row.get(FlightCSVMapping.DURATION, '0')
            days_left = row.get(FlightCSVMapping.DAYS_LEFT, '1')
            price_inr = row.get(FlightCSVMapping.PRICE, '0')
            departure_time = row.get(FlightCSVMapping.DEPARTURE_TIME, 'Morning')
            arrival_time = row.get(FlightCSVMapping.ARRIVAL_TIME, 'Morning')
            
            # Skip invalid rows
            if not source or not destination or not airline:
                return None
            
            # Parse price (remove commas and convert to float)
            price_str = str(price_inr).replace(',', '').strip()
            price_inr_float = float(price_str) if price_str else 0
            price_usd = round(price_inr_float * cls.INR_TO_USD, 2)
            
            # Parse stops
            stops = cls.STOPS_MAP.get(stops_str, 0)
            
            # Parse duration (it's in hours as float)
            duration_hours = float(duration) if duration else 2.0
            duration_str = f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m"
            
            # Calculate departure date from days_left
            days = int(float(days_left)) if days_left else 1
            departure_date = datetime.now().date() + timedelta(days=days)
            
            # Create listing ID
            listing_id = f"FL-{source[:3]}-{destination[:3]}-{flight}-{row_index}"
            
            return NormalizedListing(
                listing_id=listing_id,
                listing_type=ListingType.FLIGHT,
                name=f"{source} → {destination}",
                provider=airline,
                price=price_usd,
                currency="USD",
                date=departure_date,
                location=destination,
                metadata={
                    'origin': source,
                    'destination': destination,
                    'flight_number': flight,
                    'stops': stops,
                    'duration': duration_str,
                    'duration_hours': duration_hours,
                    'fare_class': fare_class,
                    'departure_time': cls.TIME_MAP.get(departure_time, '08:00'),
                    'arrival_time': cls.TIME_MAP.get(arrival_time, '12:00'),
                    'days_left': days,
                    'original_price_inr': price_inr_float
                }
            )
        except Exception as e:
            logger.warning(f"Failed to parse flight row {row_index}: {e}")
            return None


class AirbnbCSVParser:
    """Parser for Inside Airbnb listings CSV"""
    
    # Room type to amenity tags mapping
    ROOM_TYPE_TAGS = {
        'Entire home/apt': ['entire_home', 'private'],
        'Private room': ['private_room'],
        'Shared room': ['shared_room'],
        'Hotel room': ['hotel_room']
    }
    
    @classmethod
    def parse_row(cls, row: Dict[str, Any], row_index: int = 0) -> Optional[NormalizedListing]:
        """Parse a single CSV row to NormalizedListing"""
        try:
            listing_id = str(row.get(AirbnbCSVMapping.ID, '')).strip()
            name = row.get(AirbnbCSVMapping.NAME, '').strip()
            neighbourhood_group = row.get(AirbnbCSVMapping.NEIGHBOURHOOD_GROUP, '').strip()
            neighbourhood = row.get(AirbnbCSVMapping.NEIGHBOURHOOD, '').strip()
            room_type = row.get(AirbnbCSVMapping.ROOM_TYPE, '').strip()
            price = row.get(AirbnbCSVMapping.PRICE, '0')
            availability = row.get(AirbnbCSVMapping.AVAILABILITY_365, '365')
            number_of_reviews = row.get(AirbnbCSVMapping.NUMBER_OF_REVIEWS, '0')
            reviews_per_month = row.get(AirbnbCSVMapping.REVIEWS_PER_MONTH, '0')
            host_name = row.get(AirbnbCSVMapping.HOST_NAME, 'Host').strip()
            minimum_nights = row.get(AirbnbCSVMapping.MINIMUM_NIGHTS, '1')
            latitude = row.get(AirbnbCSVMapping.LATITUDE, '')
            longitude = row.get(AirbnbCSVMapping.LONGITUDE, '')
            
            # Skip invalid rows
            if not listing_id or not name:
                return None
            
            # Parse price (handle string with currency symbol)
            price_str = str(price).replace('$', '').replace(',', '').strip()
            price_float = float(price_str) if price_str else 0
            
            # Skip listings with 0 price
            if price_float <= 0:
                return None
            
            # Parse availability
            avail = int(float(availability)) if availability else 365
            
            # Determine location
            location = f"{neighbourhood_group}, {neighbourhood}" if neighbourhood_group else neighbourhood
            
            # Generate amenities based on room type (real data doesn't have amenities column)
            amenities = cls.ROOM_TYPE_TAGS.get(room_type, [])
            
            # Add some typical NYC amenities based on price
            if price_float > 150:
                amenities.extend(['doorman', 'gym'])
            if price_float > 100:
                amenities.append('wifi')
            if neighbourhood_group in ['Manhattan', 'Brooklyn']:
                amenities.append('near_transit')
            
            # Calculate a pseudo star rating based on reviews
            reviews = float(reviews_per_month) if reviews_per_month else 0
            num_reviews = int(float(number_of_reviews)) if number_of_reviews else 0
            star_rating = min(5, max(1, int(3 + reviews / 2))) if reviews > 0 else 3
            
            return NormalizedListing(
                listing_id=f"ABB-{listing_id}",
                listing_type=ListingType.HOTEL,
                name=name[:100],  # Truncate long names
                provider=f"Airbnb - {host_name[:30]}",
                price=price_float,
                currency="USD",
                date=datetime.now().date(),  # Current date for availability
                location=location,
                metadata={
                    'neighbourhood_group': neighbourhood_group,
                    'neighbourhood': neighbourhood,
                    'room_type': room_type,
                    'availability': avail,
                    'minimum_nights': int(float(minimum_nights)) if minimum_nights else 1,
                    'number_of_reviews': num_reviews,
                    'reviews_per_month': reviews,
                    'amenities': amenities,
                    'star_rating': star_rating,
                    'latitude': float(latitude) if latitude else None,
                    'longitude': float(longitude) if longitude else None,
                    'source': 'airbnb'
                }
            )
        except Exception as e:
            logger.warning(f"Failed to parse Airbnb row {row_index}: {e}")
            return None


class HotelBookingCSVParser:
    """Parser for Hotel Booking dataset"""
    
    # Month name to number mapping
    MONTH_MAP = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    # Meal type to amenities
    MEAL_AMENITIES = {
        'BB': ['breakfast_included'],
        'FB': ['breakfast_included', 'lunch_included', 'dinner_included'],
        'HB': ['breakfast_included', 'dinner_included'],
        'SC': [],  # Self-catering
        'Undefined': []
    }
    
    @classmethod
    def parse_row(cls, row: Dict[str, Any], row_index: int = 0) -> Optional[NormalizedListing]:
        """Parse a single CSV row to NormalizedListing"""
        try:
            hotel_type = row.get(HotelBookingCSVMapping.HOTEL, '').strip()
            is_canceled = row.get(HotelBookingCSVMapping.IS_CANCELED, '0')
            year = row.get(HotelBookingCSVMapping.ARRIVAL_DATE_YEAR, '')
            month = row.get(HotelBookingCSVMapping.ARRIVAL_DATE_MONTH, '')
            day = row.get(HotelBookingCSVMapping.ARRIVAL_DATE_DAY, '')
            adr = row.get(HotelBookingCSVMapping.ADR, '0')
            meal = row.get(HotelBookingCSVMapping.MEAL, 'SC').strip()
            country = row.get(HotelBookingCSVMapping.COUNTRY, '').strip()
            deposit_type = row.get(HotelBookingCSVMapping.DEPOSIT_TYPE, '').strip()
            reserved_room_type = row.get(HotelBookingCSVMapping.RESERVED_ROOM_TYPE, '').strip()
            adults = row.get(HotelBookingCSVMapping.ADULTS, '2')
            children = row.get(HotelBookingCSVMapping.CHILDREN, '0')
            stays_weekend = row.get(HotelBookingCSVMapping.STAYS_WEEKEND, '0')
            stays_week = row.get(HotelBookingCSVMapping.STAYS_WEEK, '0')
            
            # Skip canceled bookings for deal analysis
            if str(is_canceled) == '1':
                return None
            
            # Parse date
            try:
                month_num = cls.MONTH_MAP.get(month, 1)
                year_int = int(year) if year else 2024
                day_int = int(day) if day else 1
                
                # Use current year if historical data
                if year_int < 2024:
                    year_int = 2025
                
                arrival_date = date(year_int, month_num, day_int)
            except ValueError:
                arrival_date = datetime.now().date() + timedelta(days=random.randint(1, 90))
            
            # Parse ADR (Average Daily Rate)
            adr_str = str(adr).replace(',', '').strip()
            price = float(adr_str) if adr_str else 0
            
            # Skip very low/high prices (likely errors)
            if price < 10 or price > 5000:
                return None
            
            # Calculate total nights
            total_nights = int(float(stays_weekend or 0)) + int(float(stays_week or 0))
            if total_nights == 0:
                total_nights = 1
            
            # Determine star rating based on hotel type and price
            if hotel_type == 'Resort Hotel':
                star_rating = 4 if price > 150 else 3
            else:
                star_rating = 4 if price > 120 else 3
            
            # Determine amenities
            amenities = cls.MEAL_AMENITIES.get(meal, []).copy()
            if hotel_type == 'Resort Hotel':
                amenities.extend(['pool', 'spa', 'restaurant'])
            if price > 150:
                amenities.extend(['gym', 'wifi', 'room_service'])
            
            # Determine refundability
            is_refundable = deposit_type != 'Non Refund'
            if is_refundable:
                amenities.append('refundable')
            
            # Create listing ID
            listing_id = f"HB-{hotel_type[:3]}-{arrival_date.isoformat()}-{row_index}"
            
            # Create hotel name
            hotel_name = f"{hotel_type} - {country}" if country else hotel_type
            
            return NormalizedListing(
                listing_id=listing_id,
                listing_type=ListingType.HOTEL,
                name=hotel_name,
                provider=hotel_type,
                price=price,
                currency="USD",  # Assuming EUR, but using as is
                date=arrival_date,
                location=country if country else "Portugal",  # Default to Portugal (dataset origin)
                metadata={
                    'hotel_type': hotel_type,
                    'room_type': reserved_room_type,
                    'meal_plan': meal,
                    'total_nights': total_nights,
                    'adults': int(float(adults)) if adults else 2,
                    'children': int(float(children or 0)),
                    'amenities': amenities,
                    'star_rating': star_rating,
                    'is_refundable': is_refundable,
                    'deposit_type': deposit_type,
                    'availability': random.randint(1, 20),  # Simulated
                    'source': 'hotel_booking'
                }
            )
        except Exception as e:
            logger.warning(f"Failed to parse hotel booking row {row_index}: {e}")
            return None


# ========================================
# CSV Ingestion Service
# ========================================

class CSVIngestionStats(BaseModel):
    """Statistics for CSV ingestion"""
    total_rows: int = 0
    processed_rows: int = 0
    failed_rows: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return (self.processed_rows / self.total_rows) * 100
    
    @property
    def duration_seconds(self) -> float:
        if not self.start_time or not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()


class CSVIngestionService:
    """Service for ingesting CSV feeds"""
    
    # Parser registry
    PARSERS = {
        'flight': FlightCSVParser,
        'airbnb': AirbnbCSVParser,
        'hotel_booking': HotelBookingCSVParser,
    }
    
    # File type detection patterns
    FILE_PATTERNS = {
        r'flight|clean_dataset': 'flight',
        r'listings|airbnb': 'airbnb',
        r'hotel_booking|booking': 'hotel_booking',
    }
    
    @classmethod
    def detect_feed_type(cls, filename: str) -> Optional[str]:
        """Auto-detect feed type from filename"""
        filename_lower = filename.lower()
        for pattern, feed_type in cls.FILE_PATTERNS.items():
            if re.search(pattern, filename_lower):
                return feed_type
        return None
    
    @classmethod
    def parse_csv_file(
        cls,
        file_path: str,
        feed_type: Optional[str] = None,
        max_rows: Optional[int] = None,
        sample_rate: float = 1.0
    ) -> Generator[NormalizedListing, None, CSVIngestionStats]:
        """
        Parse a CSV file and yield NormalizedListings.
        
        Args:
            file_path: Path to CSV file
            feed_type: Type of feed (flight, airbnb, hotel_booking)
            max_rows: Maximum rows to process (None = all)
            sample_rate: Fraction of rows to process (0.0-1.0)
        
        Yields:
            NormalizedListing objects
        
        Returns:
            CSVIngestionStats after processing
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Auto-detect feed type if not provided
        if not feed_type:
            feed_type = cls.detect_feed_type(path.name)
            if not feed_type:
                raise ValueError(f"Could not detect feed type for {path.name}. Please specify feed_type.")
        
        # Get parser
        parser_class = cls.PARSERS.get(feed_type)
        if not parser_class:
            raise ValueError(f"Unknown feed type: {feed_type}")
        
        logger.info(f"Parsing {file_path} as {feed_type} feed")
        
        stats = CSVIngestionStats(start_time=datetime.utcnow())
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            
            for row_index, row in enumerate(reader):
                stats.total_rows += 1
                
                # Apply max_rows limit
                if max_rows and stats.total_rows > max_rows:
                    break
                
                # Apply sampling
                if sample_rate < 1.0 and random.random() > sample_rate:
                    continue
                
                # Parse row
                listing = parser_class.parse_row(row, row_index)
                
                if listing:
                    stats.processed_rows += 1
                    yield listing
                else:
                    stats.failed_rows += 1
                
                # Progress logging
                if stats.total_rows % 10000 == 0:
                    logger.info(f"Processed {stats.total_rows} rows...")
        
        stats.end_time = datetime.utcnow()
        logger.info(
            f"Ingestion complete: {stats.processed_rows}/{stats.total_rows} rows "
            f"({stats.success_rate:.1f}%) in {stats.duration_seconds:.2f}s"
        )
        
        return stats
    
    @classmethod
    def parse_csv_content(
        cls,
        content: str,
        feed_type: str,
        max_rows: Optional[int] = None
    ) -> Generator[NormalizedListing, None, CSVIngestionStats]:
        """Parse CSV content from string"""
        parser_class = cls.PARSERS.get(feed_type)
        if not parser_class:
            raise ValueError(f"Unknown feed type: {feed_type}")
        
        stats = CSVIngestionStats(start_time=datetime.utcnow())
        
        reader = csv.DictReader(StringIO(content))
        
        for row_index, row in enumerate(reader):
            stats.total_rows += 1
            
            if max_rows and stats.total_rows > max_rows:
                break
            
            listing = parser_class.parse_row(row, row_index)
            
            if listing:
                stats.processed_rows += 1
                yield listing
            else:
                stats.failed_rows += 1
        
        stats.end_time = datetime.utcnow()
        return stats


# ========================================
# Batch Processing Helper
# ========================================

def process_csv_in_batches(
    file_path: str,
    feed_type: Optional[str] = None,
    batch_size: int = 1000,
    max_rows: Optional[int] = None
) -> Generator[List[NormalizedListing], None, None]:
    """
    Process CSV file in batches for memory efficiency.
    
    Yields batches of NormalizedListings.
    """
    batch = []
    
    for listing in CSVIngestionService.parse_csv_file(file_path, feed_type, max_rows):
        batch.append(listing)
        
        if len(batch) >= batch_size:
            yield batch
            batch = []
    
    # Yield remaining items
    if batch:
        yield batch

