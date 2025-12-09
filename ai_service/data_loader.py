"""
Data Loader for AI Service - Loads and processes existing CSV datasets
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads and processes flight, hotel, and Airbnb listing data."""
    
    def __init__(self, data_dir: str = None):
        # Try Docker mounted path first, fall back to local path
        if data_dir is None:
            data_dir = "/app/datasets" if Path("/app/datasets").exists() else "/Users/sujithdugyala/Desktop/data 236 project datasets "
        self.data_dir = Path(data_dir)
        self.flight_data = None
        self.hotel_data = None
        self.airbnb_data = None
        
    def load_all_datasets(self):
        """Load all available datasets."""
        logger.info("Loading all datasets...")
        
        try:
            self.flight_data = self.load_flight_data()
            logger.info(f"✅ Loaded {len(self.flight_data)} flight records")
        except Exception as e:
            logger.error(f"Failed to load flight data: {e}")
            
        try:
            self.hotel_data = self.load_hotel_data()
            logger.info(f"✅ Loaded {len(self.hotel_data)} hotel records")
        except Exception as e:
            logger.error(f"Failed to load hotel data: {e}")
            
        try:
            self.airbnb_data = self.load_airbnb_data()
            logger.info(f"✅ Loaded {len(self.airbnb_data)} Airbnb listings")
        except Exception as e:
            logger.error(f"Failed to load Airbnb data: {e}")
            
        return {
            'flights': self.flight_data,
            'hotels': self.hotel_data,
            'airbnb': self.airbnb_data
        }
    
    def load_flight_data(self) -> pd.DataFrame:
        """Load and process flight price data."""
        # Load all flight CSVs
        clean_df = pd.read_csv(self.data_dir / "flight prices Clean_Dataset.csv")
        business_df = pd.read_csv(self.data_dir / "flight prices business.csv")
        economy_df = pd.read_csv(self.data_dir / "flight prices economy.csv")
        
        # Combine all flight data
        flight_df = pd.concat([clean_df, business_df, economy_df], ignore_index=True)
        
        # Remove duplicates
        flight_df = flight_df.drop_duplicates()
        
        # Clean column names
        flight_df.columns = flight_df.columns.str.strip()
        
        # Convert price to numeric (remove any non-numeric characters)
        flight_df['price'] = pd.to_numeric(flight_df['price'], errors='coerce')
        flight_df = flight_df[flight_df['price'].notna()]
        
        # Add date simulation for recent dates
        base_date = datetime.now()
        # Handle NaN values in days_left
        flight_df['days_left'] = flight_df['days_left'].fillna(7)  # Default to 7 days
        flight_df['departure_date'] = [
            base_date + timedelta(days=int(days)) 
            for days in flight_df['days_left']
        ]
        
        # Calculate 30-day rolling average price for deal detection
        flight_df['price_30d_avg'] = flight_df.groupby(
            ['source_city', 'destination_city', 'class']
        )['price'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
        
        # Calculate deal score (lower price = higher score)
        flight_df['deal_score'] = np.where(
            flight_df['price'] <= 0.85 * flight_df['price_30d_avg'],
            ((flight_df['price_30d_avg'] - flight_df['price']) / flight_df['price_30d_avg'] * 100).round(0),
            0
        )
        
        # Tag limited availability (assuming stops affect availability)
        flight_df['limited_availability'] = flight_df['stops'].apply(
            lambda x: True if x != 'zero' else False
        )
        
        # Standardize city names to airport codes (simplified mapping)
        city_to_airport = {
            'Delhi': 'DEL',
            'Mumbai': 'BOM',
            'Bangalore': 'BLR',
            'Kolkata': 'CCU',
            'Hyderabad': 'HYD',
            'Chennai': 'MAA'
        }
        
        flight_df['departure_airport'] = flight_df['source_city'].map(city_to_airport)
        flight_df['arrival_airport'] = flight_df['destination_city'].map(city_to_airport)
        
        return flight_df
    
    def load_hotel_data(self) -> pd.DataFrame:
        """Load and process hotel booking data."""
        hotel_df = pd.read_csv(self.data_dir / "hotel_booking 2.csv")
        
        # Clean column names
        hotel_df.columns = hotel_df.columns.str.strip()
        
        # Remove rows with missing prices
        hotel_df = hotel_df[hotel_df['adr'].notna()]
        
        # Calculate nightly rate (adr = average daily rate)
        hotel_df['price_per_night'] = hotel_df['adr']
        
        # Calculate total stay nights
        hotel_df['total_nights'] = (
            hotel_df['stays_in_weekend_nights'] + 
            hotel_df['stays_in_week_nights']
        )
        
        # Create arrival date
        hotel_df['arrival_date'] = pd.to_datetime(
            hotel_df['arrival_date_year'].astype(str) + '-' +
            hotel_df['arrival_date_month'] + '-' +
            hotel_df['arrival_date_day_of_month'].astype(str),
            errors='coerce'
        )
        
        # Calculate 30-day average price by hotel and room type
        hotel_df['price_30d_avg'] = hotel_df.groupby(
            ['hotel', 'reserved_room_type', 'country']
        )['adr'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
        
        # Calculate deal score
        hotel_df['deal_score'] = np.where(
            hotel_df['adr'] <= 0.85 * hotel_df['price_30d_avg'],
            ((hotel_df['price_30d_avg'] - hotel_df['adr']) / hotel_df['price_30d_avg'] * 100).round(0),
            0
        )
        
        # Tag special deals
        hotel_df['is_deal'] = hotel_df['deal_score'] >= 15
        
        # Extract amenities from meal type
        hotel_df['includes_breakfast'] = hotel_df['meal'].str.contains('BB|HB|FB', regex=True)
        
        # Tag limited availability (low deposit = more attractive)
        hotel_df['limited_availability'] = hotel_df['deposit_type'] == 'No Deposit'
        
        return hotel_df
    
    def load_airbnb_data(self) -> pd.DataFrame:
        """Load and process Airbnb listing data."""
        # Try loading the largest listings file first
        listings_files = ['listings 2.csv', 'listings.csv', 'listings 3.csv']
        
        airbnb_df = None
        for file in listings_files:
            try:
                df = pd.read_csv(self.data_dir / file, low_memory=False)
                if airbnb_df is None:
                    airbnb_df = df
                else:
                    airbnb_df = pd.concat([airbnb_df, df], ignore_index=True)
            except Exception as e:
                logger.warning(f"Could not load {file}: {e}")
        
        if airbnb_df is None:
            raise ValueError("No Airbnb data could be loaded")
        
        # Remove duplicates
        airbnb_df = airbnb_df.drop_duplicates(subset=['id'], keep='first')
        
        # Clean column names
        airbnb_df.columns = airbnb_df.columns.str.strip()
        
        # Ensure price column is numeric
        if 'price' in airbnb_df.columns:
            # Remove $ and convert to float
            airbnb_df['price'] = airbnb_df['price'].replace({r'[\$,]': ''}, regex=True)
            airbnb_df['price'] = pd.to_numeric(airbnb_df['price'], errors='coerce')
            airbnb_df = airbnb_df[airbnb_df['price'].notna()]
        
        # Calculate 30-day average price by neighbourhood
        # Handle missing neighbourhood or room_type
        airbnb_df['neighbourhood'] = airbnb_df['neighbourhood'].fillna('Unknown')
        airbnb_df['room_type'] = airbnb_df['room_type'].fillna('Unknown')
        
        airbnb_df['price_30d_avg'] = airbnb_df.groupby(
            ['neighbourhood', 'room_type']
        )['price'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
        
        # Calculate deal score
        airbnb_df['deal_score'] = np.where(
            airbnb_df['price'] <= 0.85 * airbnb_df['price_30d_avg'],
            ((airbnb_df['price_30d_avg'] - airbnb_df['price']) / airbnb_df['price_30d_avg'] * 100).round(0),
            0
        )
        
        # Tag limited availability (high minimum nights = less flexible)
        airbnb_df['limited_availability'] = airbnb_df['availability_365'] < 30
        
        # Tag popular listings (high reviews = popular)
        airbnb_df['is_popular'] = airbnb_df['number_of_reviews'] > airbnb_df['number_of_reviews'].median()
        
        # Extract amenities
        airbnb_df['entire_home'] = airbnb_df['room_type'] == 'Entire home/apt'
        
        return airbnb_df
    
    def get_flight_deals(self, min_discount: float = 15.0, limit: int = 50) -> List[Dict]:
        """Get current flight deals."""
        if self.flight_data is None:
            self.load_flight_data()
        
        deals = self.flight_data[self.flight_data['deal_score'] >= min_discount].copy()
        deals = deals.sort_values('deal_score', ascending=False).head(limit)
        
        return deals.to_dict('records')
    
    def get_hotel_deals(self, min_discount: float = 15.0, limit: int = 50) -> List[Dict]:
        """Get current hotel deals."""
        if self.hotel_data is None:
            self.load_hotel_data()
        
        deals = self.hotel_data[self.hotel_data['deal_score'] >= min_discount].copy()
        deals = deals.sort_values('deal_score', ascending=False).head(limit)
        
        return deals.to_dict('records')
    
    def get_airbnb_deals(self, min_discount: float = 15.0, limit: int = 50) -> List[Dict]:
        """Get current Airbnb deals."""
        if self.airbnb_data is None:
            self.load_airbnb_data()
        
        deals = self.airbnb_data[self.airbnb_data['deal_score'] >= min_discount].copy()
        deals = deals.sort_values('deal_score', ascending=False).head(limit)
        
        return deals.to_dict('records')
    
    def search_flights(
        self, 
        source: Optional[str] = None,
        destination: Optional[str] = None,
        max_price: Optional[float] = None,
        flight_class: Optional[str] = None
    ) -> pd.DataFrame:
        """Search flights with filters."""
        if self.flight_data is None:
            self.load_flight_data()
        
        df = self.flight_data.copy()
        
        if source:
            df = df[df['source_city'].str.contains(source, case=False, na=False)]
        
        if destination:
            df = df[df['destination_city'].str.contains(destination, case=False, na=False)]
        
        if max_price:
            df = df[df['price'] <= max_price]
        
        if flight_class:
            df = df[df['class'].str.lower() == flight_class.lower()]
        
        return df
    
    def search_hotels(
        self,
        city: Optional[str] = None,
        max_price: Optional[float] = None,
        includes_breakfast: Optional[bool] = None
    ) -> pd.DataFrame:
        """Search hotels with filters."""
        if self.hotel_data is None:
            self.load_hotel_data()
        
        df = self.hotel_data.copy()
        
        if city:
            df = df[df['country'].str.contains(city, case=False, na=False)]
        
        if max_price:
            df = df[df['adr'] <= max_price]
        
        if includes_breakfast is not None:
            df = df[df['includes_breakfast'] == includes_breakfast]
        
        return df
    
    def get_statistics(self) -> Dict:
        """Get dataset statistics."""
        stats = {
            'flights': {
                'total_records': len(self.flight_data) if self.flight_data is not None else 0,
                'unique_routes': 0,
                'avg_price': 0,
                'deals_count': 0
            },
            'hotels': {
                'total_records': len(self.hotel_data) if self.hotel_data is not None else 0,
                'unique_hotels': 0,
                'avg_price': 0,
                'deals_count': 0
            },
            'airbnb': {
                'total_records': len(self.airbnb_data) if self.airbnb_data is not None else 0,
                'unique_neighbourhoods': 0,
                'avg_price': 0,
                'deals_count': 0
            }
        }
        
        if self.flight_data is not None:
            stats['flights']['unique_routes'] = len(
                self.flight_data[['source_city', 'destination_city']].drop_duplicates()
            )
            stats['flights']['avg_price'] = float(self.flight_data['price'].mean())
            stats['flights']['deals_count'] = int((self.flight_data['deal_score'] >= 15).sum())
        
        if self.hotel_data is not None:
            stats['hotels']['unique_hotels'] = int(self.hotel_data['hotel'].nunique())
            stats['hotels']['avg_price'] = float(self.hotel_data['adr'].mean())
            stats['hotels']['deals_count'] = int((self.hotel_data['deal_score'] >= 15).sum())
        
        if self.airbnb_data is not None:
            stats['airbnb']['unique_neighbourhoods'] = int(self.airbnb_data['neighbourhood'].nunique())
            stats['airbnb']['avg_price'] = float(self.airbnb_data['price'].mean())
            stats['airbnb']['deals_count'] = int((self.airbnb_data['deal_score'] >= 15).sum())
        
        return stats


# Test the loader
if __name__ == "__main__":
    loader = DatasetLoader()
    
    print("🔄 Loading datasets...")
    datasets = loader.load_all_datasets()
    
    print("\n📊 Dataset Statistics:")
    stats = loader.get_statistics()
    
    print(f"\n✈️  Flights:")
    print(f"  Total: {stats['flights']['total_records']:,}")
    print(f"  Unique Routes: {stats['flights']['unique_routes']:,}")
    print(f"  Avg Price: ${stats['flights']['avg_price']:.2f}")
    print(f"  Deals Available: {stats['flights']['deals_count']:,}")
    
    print(f"\n🏨 Hotels:")
    print(f"  Total: {stats['hotels']['total_records']:,}")
    print(f"  Unique Hotels: {stats['hotels']['unique_hotels']:,}")
    print(f"  Avg Price: ${stats['hotels']['avg_price']:.2f}")
    print(f"  Deals Available: {stats['hotels']['deals_count']:,}")
    
    print(f"\n🏠 Airbnb:")
    print(f"  Total: {stats['airbnb']['total_records']:,}")
    print(f"  Unique Neighbourhoods: {stats['airbnb']['unique_neighbourhoods']:,}")
    print(f"  Avg Price: ${stats['airbnb']['avg_price']:.2f}")
    print(f"  Deals Available: {stats['airbnb']['deals_count']:,}")
    
    print("\n🎉 Top 5 Flight Deals:")
    flight_deals = loader.get_flight_deals(limit=5)
    for i, deal in enumerate(flight_deals, 1):
        print(f"  {i}. {deal['airline']} {deal['source_city']}→{deal['destination_city']} "
              f"${deal['price']} (Save {deal['deal_score']:.0f}%)")
    
    print("\n🎉 Top 5 Hotel Deals:")
    hotel_deals = loader.get_hotel_deals(limit=5)
    for i, deal in enumerate(hotel_deals, 1):
        print(f"  {i}. {deal['hotel']} {deal['country']} "
              f"${deal['adr']:.2f}/night (Save {deal['deal_score']:.0f}%)")
