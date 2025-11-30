"""
Test script for CSV ingestion with actual Kaggle datasets
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_service.deals_agent import DealsAgent
from ai_service.csv_ingestion import CSVIngestionService

async def test_csv_ingestion():
    """Test CSV ingestion with actual data"""
    
    print("=" * 80)
    print("CSV FEED INGESTION TEST")
    print("=" * 80)
    
    # Initialize Deals Agent
    deals_agent = DealsAgent()
    await deals_agent.start()
    
    print("\n✓ Deals Agent started successfully")
    
    # Test files
    feeds_dir = Path("data/feeds")
    
    if not feeds_dir.exists():
        print(f"\n❌ Error: {feeds_dir} directory not found")
        return
    
    csv_files = list(feeds_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"\n❌ Error: No CSV files found in {feeds_dir}")
        return
    
    print(f"\n📁 Found {len(csv_files)} CSV files:")
    for f in csv_files:
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"  • {f.name} ({size_mb:.1f} MB)")
    
    print("\n" + "=" * 80)
    print("INGESTING CSV FILES (Limited to 5,000 rows per file for testing)")
    print("=" * 80)
    
    results = {}
    
    for csv_file in csv_files:
        print(f"\n📊 Processing: {csv_file.name}")
        print("-" * 80)
        
        try:
            # Detect feed type
            feed_type = CSVIngestionService.detect_feed_type(csv_file.name)
            
            if not feed_type:
                print(f"  ⚠️  Could not detect feed type, skipping...")
                continue
            
            print(f"  • Detected type: {feed_type}")
            print(f"  • Starting ingestion...")
            
            # Ingest with limits for testing
            stats = await deals_agent.ingest_csv_file(
                str(csv_file),
                feed_type=feed_type,
                max_rows=5000,  # Limit for testing
                batch_size=500,
                sample_rate=1.0  # Use all rows within max_rows
            )
            
            results[csv_file.name] = stats
            
            print(f"\n  ✓ Ingestion complete!")
            print(f"    - Total rows read: {stats.total_rows}")
            print(f"    - Successfully processed: {stats.processed_rows}")
            print(f"    - Failed: {stats.failed_rows}")
            print(f"    - Success rate: {stats.success_rate:.1f}%")
            print(f"    - Duration: {stats.duration_seconds:.2f} seconds")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Get cached deals
    print("\n" + "=" * 80)
    print("CACHED DEALS SUMMARY")
    print("=" * 80)
    
    all_deals = deals_agent.get_cached_deals(limit=10000)
    flight_deals = deals_agent.get_cached_deals(limit=10000, listing_type="flight")
    hotel_deals = deals_agent.get_cached_deals(limit=10000, listing_type="hotel")
    
    print(f"\n📦 Total cached deals: {len(all_deals)}")
    print(f"  • Flight deals: {len(flight_deals)}")
    print(f"  • Hotel deals: {len(hotel_deals)}")
    
    if all_deals:
        print(f"\n🏆 Top 10 Deals (by score):")
        print("-" * 80)
        for i, deal in enumerate(all_deals[:10], 1):
            print(f"{i:2d}. [{deal.deal_score:3d}] {deal.deal.name[:50]:<50} ${deal.deal.price:>8.2f}")
            tags = ', '.join([t.value for t in deal.tags[:3]])
            print(f"     Tags: {tags}")
            print(f"     Why: {deal.why_this[:70]}")
            print()
    
    # Stop agent
    await deals_agent.stop()
    print("\n✓ Deals Agent stopped")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_csv_ingestion())

