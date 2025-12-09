"""
Test script for data loader and deals agent with CSV datasets.
Run with: python ai_service/test_data_loader.py
"""
import asyncio
import sys
import os

# Add ai_service to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import DatasetLoader
from agents.deals_agent import DealsAgent


async def test_data_loader():
    """Test the data loader."""
    print("=" * 80)
    print("TESTING DATA LOADER")
    print("=" * 80)
    
    loader = DatasetLoader()
    
    print("\n📦 Loading datasets...")
    datasets = loader.load_all_datasets()
    
    print("\n📊 Dataset Statistics:")
    stats = loader.get_statistics()
    
    print(f"\n✈️  Flights:")
    print(f"  Total Records: {stats['flights']['total_records']:,}")
    print(f"  Unique Routes: {stats['flights']['unique_routes']:,}")
    print(f"  Average Price: ${stats['flights']['avg_price']:.2f}")
    print(f"  Deals Available: {stats['flights']['deals_count']:,}")
    
    print(f"\n🏨 Hotels:")
    print(f"  Total Records: {stats['hotels']['total_records']:,}")
    print(f"  Unique Hotels: {stats['hotels']['unique_hotels']:,}")
    print(f"  Average Price: ${stats['hotels']['avg_price']:.2f}")
    print(f"  Deals Available: {stats['hotels']['deals_count']:,}")
    
    print(f"\n🏠 Airbnb:")
    print(f"  Total Records: {stats['airbnb']['total_records']:,}")
    print(f"  Unique Neighbourhoods: {stats['airbnb']['unique_neighbourhoods']:,}")
    print(f"  Average Price: ${stats['airbnb']['avg_price']:.2f}")
    print(f"  Deals Available: {stats['airbnb']['deals_count']:,}")
    
    # Test flight deals
    print("\n" + "=" * 80)
    print("TOP 10 FLIGHT DEALS")
    print("=" * 80)
    flight_deals = loader.get_flight_deals(min_discount=15.0, limit=10)
    for i, deal in enumerate(flight_deals, 1):
        print(f"\n{i}. {deal['airline']} - {deal['source_city']} → {deal['destination_city']}")
        print(f"   Price: ${deal['price']:.2f} (was ${deal['price_30d_avg']:.2f})")
        print(f"   Save: {deal['deal_score']:.0f}%")
        print(f"   Class: {deal['class']} | Stops: {deal['stops']}")
    
    # Test hotel deals
    print("\n" + "=" * 80)
    print("TOP 10 HOTEL DEALS")
    print("=" * 80)
    hotel_deals = loader.get_hotel_deals(min_discount=15.0, limit=10)
    for i, deal in enumerate(hotel_deals, 1):
        print(f"\n{i}. {deal['hotel']} - {deal['country']}")
        print(f"   Price: ${deal['adr']:.2f}/night (was ${deal['price_30d_avg']:.2f})")
        print(f"   Save: {deal['deal_score']:.0f}%")
        print(f"   Breakfast: {'Yes' if deal['includes_breakfast'] else 'No'}")
    
    # Test Airbnb deals
    print("\n" + "=" * 80)
    print("TOP 10 AIRBNB DEALS")
    print("=" * 80)
    airbnb_deals = loader.get_airbnb_deals(min_discount=15.0, limit=10)
    for i, deal in enumerate(airbnb_deals, 1):
        print(f"\n{i}. {deal['name'][:50]}")
        print(f"   Price: ${deal['price']:.2f}/night (was ${deal['price_30d_avg']:.2f})")
        print(f"   Save: {deal['deal_score']:.0f}%")
        print(f"   Location: {deal['neighbourhood']}")
        print(f"   Type: {deal['room_type']} | Reviews: {deal['number_of_reviews']}")
    
    # Test search functionality
    print("\n" + "=" * 80)
    print("SEARCH TESTS")
    print("=" * 80)
    
    print("\n🔍 Searching flights: Delhi → Mumbai")
    search_results = loader.search_flights(source="Delhi", destination="Mumbai", max_price=7000)
    print(f"   Found: {len(search_results)} flights")
    if len(search_results) > 0:
        cheapest = search_results.nsmallest(1, 'price').iloc[0]
        print(f"   Cheapest: {cheapest['airline']} - ${cheapest['price']:.2f}")
    
    print("\n🔍 Searching hotels with breakfast")
    hotel_search = loader.search_hotels(includes_breakfast=True, max_price=100)
    print(f"   Found: {len(hotel_search)} hotels with breakfast under $100")
    
    return loader


async def test_deals_agent(loader):
    """Test the deals agent."""
    print("\n" + "=" * 80)
    print("TESTING DEALS AGENT")
    print("=" * 80)
    
    print("\n⚙️  Initializing Deals Agent...")
    agent = DealsAgent()
    
    print("\n🔍 Scanning for deals...")
    await agent.scan_for_deals()
    
    print("\n📦 Cached Deals Summary:")
    all_deals = agent.get_cached_deals()
    print(f"  Total Deals: {len(all_deals)}")
    
    flight_deals = agent.get_cached_deals(listing_type="flight")
    hotel_deals = agent.get_cached_deals(listing_type="hotel")
    airbnb_deals = agent.get_cached_deals(listing_type="airbnb")
    
    print(f"  Flight Deals: {len(flight_deals)}")
    print(f"  Hotel Deals: {len(hotel_deals)}")
    print(f"  Airbnb Deals: {len(airbnb_deals)}")
    
    print("\n🏆 Top 5 Deals by Score:")
    top_deals = all_deals[:5]
    for i, deal in enumerate(top_deals, 1):
        print(f"\n{i}. {deal.get('listing_type', '').upper()}: {deal.get('name', deal.get('route', 'N/A'))}")
        print(f"   Score: {deal.get('deal_score', 0):.0f}/100")
        print(f"   Price: ${deal.get('current_price', 0):.2f} (Save {deal.get('tags', [])})")
        print(f"   Tags: {', '.join(deal.get('tags', []))}")
    
    return agent


async def main():
    """Main test function."""
    print("\n🚀 Starting CSV Dataset Integration Tests...\n")
    
    try:
        # Test data loader
        loader = await test_data_loader()
        
        # Test deals agent
        agent = await test_deals_agent(loader)
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\n💡 Next Steps:")
        print("  1. Start the AI service: cd ai_service && uvicorn main:app --port 8008")
        print("  2. Access deals API: http://localhost:8008/api/deals")
        print("  3. Check API docs: http://localhost:8008/docs")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
