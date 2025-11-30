# Kayak Simulation - Travel Booking Platform

**SJSU Data 236 - Distributed Systems for Data Engineering**  
**Group Project - Team 1**

## Project Overview

This project implements a Kayak-like travel metasearch and booking platform using a distributed, service-oriented architecture. The system allows users to search, compare, filter, and book flights, hotels, and rental cars.

## Team 1 Responsibilities

- **User Service** - User registration, authentication, profile management
- **Admin Service** - Admin dashboard, user management, analytics reports
- **Client UI** - User and Admin web interfaces
- **AI Recommendation Service** - Deals Agent & Concierge Agent (FastAPI)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Tier (React)                       │
├─────────────────────────────────────────────────────────────────┤
│  User Module           │  Admin Module          │  AI Chat       │
│  - Registration        │  - Dashboard           │  - Concierge   │
│  - Login/Profile       │  - User Management     │  - Bundles     │
│  - Search/Filter       │  - Listing Management  │  - Watches     │
│  - Bookings            │  - Reports/Analytics   │               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Middleware Tier (FastAPI)                    │
├─────────────────────────────────────────────────────────────────┤
│  User Service    │  Admin Service   │  AI Service               │
│  (Port 8001)     │  (Port 8002)     │  (Port 8006)              │
│                  │                  │  - Deals Agent            │
│  ↕ Redis Cache   │  ↕ Redis Cache   │  - Concierge Agent        │
│  ↕ Kafka         │  ↕ Kafka         │  - WebSocket Events       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Tier                               │
├─────────────────────────────────────────────────────────────────┤
│  MySQL                          │  MongoDB                       │
│  - Users                        │  - Reviews                     │
│  - Admins                       │  - Logs                        │
│  - Bookings                     │  - Activity Tracking           │
│  - Billing                      │  - Images                      │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **FastAPI** - REST API framework (Python)
- **SQLAlchemy** - MySQL ORM
- **PyMongo** - MongoDB driver
- **Redis** - Caching layer
- **Kafka** - Message queue (aiokafka)
- **Pydantic v2** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Styling
- **React Query** - Server state management
- **Zustand** - Client state management
- **Framer Motion** - Animations
- **Chart.js** - Analytics charts

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local orchestration
- **MySQL 8** - Relational database
- **MongoDB 7** - Document database
- **Redis 7** - Cache
- **Kafka** - Message broker

## Project Structure

```
kayak-simulation/
├── backend/
│   ├── shared/              # Shared utilities
│   │   ├── config.py        # Configuration settings
│   │   ├── database.py      # Database connections
│   │   ├── cache.py         # Redis caching
│   │   ├── validators.py    # SSN, ZIP, State validation
│   │   └── kafka_producer.py
│   ├── user_service/        # User Service
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── routes.py
│   └── admin_service/       # Admin Service
│       ├── main.py
│       ├── models.py
│       ├── repository.py
│       ├── service.py
│       └── routes.py
├── ai_service/              # AI Recommendation Service
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── deals_agent.py       # Deal detection
│   └── concierge_agent.py   # Chat & recommendations
├── client/                  # React Frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── layouts/         # Layout components
│   │   ├── store/           # State management
│   │   └── services/        # API clients
│   ├── package.json
│   └── tailwind.config.js
├── database/
│   └── mysql/
│       └── schema.sql       # DDL scripts
├── docker/                  # Dockerfiles
├── tests/                   # Unit tests
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- MySQL 8 (or Docker)
- Redis (or Docker)

### 1. Clone and Setup

```bash
cd "data 236/group project"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Infrastructure with Docker

```bash
docker-compose up -d mysql mongodb redis kafka zookeeper
```

### 3. Initialize Database

```bash
mysql -u kayak_user -p kayak_db < database/mysql/schema.sql
```

### 4. Start Backend Services

```bash
# Terminal 1 - User Service
uvicorn backend.user_service.main:app --reload --port 8001

# Terminal 2 - Admin Service (port 8006 per Team 5's architecture)
uvicorn backend.admin_service.main:app --reload --port 8006

# Terminal 3 - AI Service (port 8008 per Team 5's architecture)
uvicorn ai_service.main:app --reload --port 8008
```

### 5. Start Frontend

```bash
cd client
npm install
npm start
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **User Service API**: http://localhost:8001/docs
- **Admin Service API**: http://localhost:8006/docs
- **AI Service API**: http://localhost:8008/docs

### Service Port Reference (Team 5 Architecture)

| Service | Port | Team |
|---------|------|------|
| User Service | 8001 | Team 1 |
| Flight Service | 8002 | Team 2 |
| Hotel Service | 8003 | Team 2 |
| Car Service | 8004 | Team 2 |
| Billing Service | 8005 | Team 4 |
| Admin Service | 8006 | Team 1 |
| Search Service | 8007 | Team 2 |
| AI Service | 8008 | Team 1 |

## API Endpoints

### User Service (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create new user |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| POST | `/users/login` | User login |
| GET | `/users/me` | Get current user |

### Admin Service (Port 8002)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/login` | Admin login |
| GET | `/admin/users` | List all users |
| PUT | `/admin/users/{id}` | Modify user |
| DELETE | `/admin/users/{id}` | Delete user |
| POST | `/admin/listings` | Add listing |
| GET | `/admin/reports/top-properties` | Top 10 properties report |
| GET | `/admin/reports/city-revenue` | City-wise revenue report |
| GET | `/admin/reports/provider-analysis` | Provider analytics |

### AI Service (Port 8006)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bundles` | Get trip bundles |
| POST | `/chat` | Chat with concierge |
| GET | `/deals` | Get current deals |
| POST | `/watches` | Create price watch |
| WS | `/events` | Real-time updates |

## Validation Rules

### User ID (SSN Format)
- Pattern: `###-##-####`
- Example: `123-45-6789`

### ZIP Code
- Valid: `#####` or `#####-####`
- Examples: `95123`, `90086-1929`
- Invalid: `1247`, `1829A`, `37849-392`

### State
- Must be valid US state abbreviation or full name
- Examples: `CA`, `California`, `NY`, `New York`

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

## Default Credentials

### Admin Login
- Email: `admin@kayak-sim.com`
- Password: `admin123`

## Kafka Topics

| Topic | Description |
|-------|-------------|
| `user.events` | User CRUD events |
| `admin.events` | Admin activity events |
| `raw_supplier_feeds` | Raw CSV feed data |
| `deals.normalized` | Normalized deals |
| `deals.scored` | Scored deals |
| `deals.tagged` | Tagged deals |
| `deal.events` | Real-time deal events |

## Redis Cache Keys

| Pattern | Description |
|---------|-------------|
| `kayak:user:{id}` | User data cache |
| `kayak:user:email:{email}` | User by email cache |
| `kayak:admin:{id}` | Admin data cache |

## Team Members

- **Team 1**: User & Admin Services + Client User UI + AI Service

## Integration Points

### Receives From:
- Team 2: Listing schemas (Flights, Hotels, Cars)
- Team 3: User booking history data format
- Team 4: Billing data for admin reports
- Team 5: Kafka connection details, Redis config

### Provides To:
- Team 2: Search request formats, AI recommendations
- Team 3: User data format, authentication flow
- Team 4: Admin billing access endpoints
- Team 5: User event payloads

## License

This project is for educational purposes - SJSU Data 236 Course.


