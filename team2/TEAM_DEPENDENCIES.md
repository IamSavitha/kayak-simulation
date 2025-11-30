# Team 2 - Dependencies and Integration Requirements

## What Team 2 Needs From Other Teams

### From Team 1 (User & Admin Services)
**Status:** ⚠️ **REQUIRED FOR INTEGRATION**

1. **Search Request Format** (Optional - can define our own)
   - How should search requests be formatted when coming from Team 1's UI?
   - Preferred: Team 1 uses our existing search endpoints directly

2. **Admin Listing Management** (Optional - can define our own)
   - Admin endpoints for listing management can use our existing CRUD endpoints
   - No special format needed

3. **AI Service Integration** (Optional - for Team 1's AI service)
   - Our listing data is accessible via our APIs
   - AI service can query our search endpoints
   - We publish listing events to Kafka for real-time updates

**Action Items:**
- ✅ **DONE**: Our APIs are ready - Team 1 can integrate directly
- ⏳ **PENDING**: Coordinate on search request format (if different from our current format)
- ⏳ **PENDING**: Coordinate on AI service data access patterns

---

### From Team 3 (Booking Service)
**Status:** ⚠️ **REQUIRED FOR INTEGRATION**

1. **Booking Availability Check Requests**
   - **Format**: Team 3 should call our availability endpoints:
     - `GET /flights/{flight_id}` - Check `current_available_seats`
     - `GET /hotels/{hotel_id}` - Check `current_available_rooms`
     - `GET /cars/{car_id}` - Check `availability_status`
   
2. **Availability Update After Booking**
   - **Format**: Team 3 should call:
     - `PUT /flights/{flight_id}/availability?seats_change=-1`
     - `PUT /hotels/{hotel_id}/availability?rooms_change=-1`
     - `PUT /cars/{car_id}/availability?status=Reserved`

3. **Rating Update After Review**
   - **Format**: Team 3 should call:
     - `PUT /flights/{flight_id}/rating?new_rating=4.5&total_reviews=100`
     - `PUT /hotels/{hotel_id}/rating?new_rating=4.5&total_reviews=100`
     - `PUT /cars/{car_id}/rating?new_rating=4.5&total_reviews=100`

**Action Items:**
- ✅ **DONE**: Availability endpoints are ready
- ⏳ **PENDING**: Team 3 needs to integrate with our endpoints
- ⏳ **PENDING**: Coordinate on error handling (what happens if availability update fails?)

---

### From Team 4 (Billing Service)
**Status:** ✅ **NO DEPENDENCIES**

1. **Listing Pricing Information**
   - Team 4 can call our GET endpoints to retrieve pricing:
     - `GET /flights/{flight_id}` - Get `ticket_price`
     - `GET /hotels/{hotel_id}` - Get `price_per_night`
     - `GET /cars/{car_id}` - Get `daily_rental_price`

**Action Items:**
- ✅ **DONE**: Pricing is available via our APIs
- ✅ **NO ACTION NEEDED**: Team 4 can integrate independently

---

### From Team 5 (Kafka Integration)
**Status:** ⚠️ **REQUIRED FOR KAFKA EVENTS**

1. **Kafka Connection Details**
   - **Required**: Kafka bootstrap server address
   - **Required**: Topic name for listing updates (we use `listing_updates`)
   - **Required**: Kafka broker configuration

2. **Redis Connection Details**
   - **Required**: Redis host and port
   - **Required**: Redis database number (if applicable)

3. **Event Schema Confirmation**
   - We publish events in this format:
   ```json
   {
     "event_type": "listing_created|listing_updated|listing_deleted",
     "listing_type": "flight|hotel|car",
     "listing_id": "...",
     "timestamp": "2024-01-01T00:00:00",
     "data": {...}
   }
   ```
   - **Action**: Confirm this format works with Team 5's consumers

**Action Items:**
- ⏳ **PENDING**: Get Kafka bootstrap server address from Team 5
- ⏳ **PENDING**: Get Redis connection details from Team 5
- ⏳ **PENDING**: Confirm event schema format
- ⏳ **PENDING**: Test Kafka connection (once Team 5 sets up Kafka)

**Current Configuration:**
- Kafka: `localhost:9092` (default, needs Team 5's actual address)
- Redis: `localhost:6379` (default, needs Team 5's actual address)
- Topic: `listing_updates` (can be changed if needed)

---

### From Team 6 (Testing & Deployment)
**Status:** ✅ **NO BLOCKING DEPENDENCIES**

1. **API Contract Format**
   - ✅ **DONE**: Our API documentation is ready (see `API_DOCUMENTATION.md`)
   - ✅ **DONE**: OpenAPI/Swagger docs available at `/docs`

2. **Docker Configuration**
   - ✅ **DONE**: Dockerfile and docker-compose.yml are ready
   - ⏳ **PENDING**: May need to coordinate on shared docker-compose for all services

3. **Test Requirements**
   - ✅ **DONE**: Unit tests are created
   - ⏳ **PENDING**: May need integration test scenarios from Team 6

**Action Items:**
- ✅ **DONE**: Docker configuration ready
- ✅ **DONE**: API documentation ready
- ⏳ **PENDING**: Coordinate on deployment configuration
- ⏳ **PENDING**: Get integration test requirements

---

## What Team 2 Provides To Other Teams

### To Team 1
- ✅ Listing schemas (documented in API docs)
- ✅ Search endpoints for user interface
- ✅ Listing data for admin reports
- ✅ Listing data access for AI deals agent (via APIs)

### To Team 3
- ✅ Listing availability endpoints
- ✅ Availability update endpoints
- ✅ Rating update endpoints

### To Team 4
- ✅ Listing pricing information (via GET endpoints)

### To Team 5
- ✅ Listing update events to Kafka:
  - `listing_created`
  - `listing_updated`
  - `listing_deleted`

### To Team 6
- ✅ API documentation
- ✅ Docker configuration
- ✅ Test files
- ✅ Database schema documentation

---

## Critical Path Items

### Must Have Before Integration:
1. **Team 5**: Kafka and Redis connection details ⚠️ **BLOCKING**
2. **Team 3**: Coordinate on availability update flow ⚠️ **BLOCKING**
3. **Team 1**: Coordinate on search request format (if different) ⚠️ **IMPORTANT**

### Nice to Have:
1. **Team 6**: Integration test scenarios
2. **Team 1**: AI service data access patterns
3. **All Teams**: Shared docker-compose configuration

---

## Contact Information

**Team 2 Lead:** Liza

**Integration Questions:**
- For API integration: See `API_DOCUMENTATION.md`
- For Kafka events: See Kafka event format above
- For database schema: See DDL files in `database/ddl/`

---

## Next Steps

1. **Immediate (Day 1-2):**
   - ✅ Complete Team 2 implementation (DONE)
   - ⏳ Get Kafka/Redis connection details from Team 5
   - ⏳ Share API documentation with Teams 1, 3, 4

2. **Integration Phase (Day 3-4):**
   - ⏳ Test Kafka connection with Team 5
   - ⏳ Coordinate with Team 3 on availability flow
   - ⏳ Coordinate with Team 1 on search integration

3. **Final Phase (Day 5-6):**
   - ⏳ Integration testing with all teams
   - ⏳ Performance testing
   - ⏳ Final documentation

