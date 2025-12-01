#!/bin/sh
# Startup script for backend services
# Uses SERVICE_NAME environment variable to determine which service to start

SERVICE_NAME=${SERVICE_NAME:-user_service}

# Map service names to their module paths
case $SERVICE_NAME in
  user_service)
    MODULE="backend.services.user_service.main"
    ;;
  flight_service)
    MODULE="backend.services.flight_service.main"
    ;;
  hotel_service)
    MODULE="backend.services.hotel_service.main"
    ;;
  car_service)
    MODULE="backend.services.car_service.main"
    ;;
  billing_service)
    MODULE="backend.services.billing_service.main"
    ;;
  admin_service)
    MODULE="backend.services.admin_service.main"
    ;;
  search_service)
    MODULE="backend.services.search_service.main"
    ;;
  *)
    echo "Unknown service: $SERVICE_NAME"
    exit 1
    ;;
esac

echo "Starting $SERVICE_NAME..."
exec uvicorn "$MODULE:app" --host 0.0.0.0 --port 8000

