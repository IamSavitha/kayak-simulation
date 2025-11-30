# Team 2 - Listing Services (Flights, Hotels, Cars)

## Architecture

This service is split into 3 separate microservices following Team 5's architecture:

| Service | Port | Description |
|---------|------|-------------|
| Flight Service | 8002 | Flight listings CRUD, search, availability |
| Hotel Service | 8003 | Hotel listings CRUD, search, images, availability |
| Car Service | 8004 | Car listings CRUD, search, availability |

## Project Structure

```
team2/
├── backend/
│   ├── common/                    # Shared utilities (Team 5 compatible)
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database connections
│   │   ├── cache.py              # Redis caching
│   │   ├── validators.py         # Input validation
│   │   └── exceptions.py         # Custom exceptions
│   ├── kafka/                     # Kafka configuration
│   │   ├── topics.py             # Topic definitions
│   │   └── producer.py           # Kafka producer
│   ├── schemas/                   # Pydantic schemas
│   │   ├── flight_schemas.py
│   │   ├── hotel_schemas.py
│   │   └── car_schemas.py
│   ├── repositories/              # Data access layer
│   │   ├── flight_repository.py
│   │   ├── hotel_repository.py
│   │   └── car_repository.py
│   └── services/                  # Microservices
│       ├── flight_service/
│       │   └── main.py           # Port 8002
│       ├── hotel_service/
│       │   └── main.py           # Port 8003
│       └── car_service/
│           └── main.py           # Port 8004
├── database/
│   └── ddl/                       # MySQL DDL scripts
├── docker/                        # Docker configurations
│   ├── Dockerfile.flight
│   ├── Dockerfile.hotel
│   └── Dockerfile.car
├── scripts/
│   └── seed_data.py              # Data seeding (10,000+ listings)
├── tests/                         # Unit tests
├── docker-compose.yml
└── requirements.txt
```

## Quick Start

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- Flight Service: http://localhost:8002
- Hotel Service: http://localhost:8003
- Car Service: http://localhost:8004
- MySQL, MongoDB, Redis, Kafka

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start each service in separate terminals
cd team2
uvicorn backend.services.flight_service.main:app --port 8002 --reload
uvicorn backend.services.hotel_service.main:app --port 8003 --reload
uvicorn backend.services.car_service.main:app --port 8004 --reload
```

### Seed Data

```bash
python scripts/seed_data.py
```

## API Endpoints

### Flight Service (Port 8002)
- `POST /flights` - Create flight
- `GET /flights/{id}` - Get flight
- `PUT /flights/{id}` - Update flight
- `DELETE /flights/{id}` - Delete flight
- `GET /flights/search` - Search flights
- `PUT /flights/{id}/availability` - Update availability
- `PUT /flights/{id}/rating` - Update rating

### Hotel Service (Port 8003)
- `POST /hotels` - Create hotel
- `GET /hotels/{id}` - Get hotel
- `PUT /hotels/{id}` - Update hotel
- `DELETE /hotels/{id}` - Delete hotel
- `GET /hotels/search` - Search hotels
- `POST /hotels/{id}/images` - Upload image
- `GET /hotels/{id}/images` - Get images
- `PUT /hotels/{id}/availability` - Update availability
- `PUT /hotels/{id}/rating` - Update rating

### Car Service (Port 8004)
- `POST /cars` - Create car
- `GET /cars/{id}` - Get car
- `PUT /cars/{id}` - Update car
- `DELETE /cars/{id}` - Delete car
- `GET /cars/search` - Search cars
- `POST /cars/{id}/images` - Upload image
- `GET /cars/{id}/images` - Get images
- `PUT /cars/{id}/availability` - Update availability
- `PUT /cars/{id}/rating` - Update rating

## Configuration

Environment variables (Docker hostnames):
- `MYSQL_HOST=mysql`
- `MONGODB_HOST=mongodb`
- `REDIS_HOST=redis`
- `KAFKA_BOOTSTRAP_SERVERS=kafka:9092`

## Integration Points

### Provides To:
- **Team 1**: Listing schemas, search endpoints, AI data access
- **Team 3**: Availability endpoints for booking
- **Team 4**: Pricing information
- **Team 5**: Kafka events (`listing_updates` topic)

### Receives From:
- **Team 5**: Kafka/Redis infrastructure

## Kafka Events

Topic: `listing_updates`

Events:
- `listing_created`
- `listing_updated`
- `listing_deleted`

## Team

**Team 2 Lead:** Liza
