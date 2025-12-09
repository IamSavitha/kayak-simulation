#!/bin/bash
# Test admin login and dashboard

echo "🔑 Testing Admin Login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8006/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@kayak.com",
    "password": "admin123"
  }')

echo "$LOGIN_RESPONSE" | jq '.'

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
  echo ""
  echo "✅ Login successful! Token: ${TOKEN:0:20}..."
  echo ""
  echo "📊 Testing Dashboard Stats..."
  curl -s -X GET "http://localhost:8006/dashboard/stats" \
    -H "Authorization: Bearer $TOKEN" | jq '.'
  
  echo ""
  echo "📋 Testing Bookings List..."
  curl -s -X GET "http://localhost:8006/bookings?page=1&page_size=5" \
    -H "Authorization: Bearer $TOKEN" | jq '.total, .bookings[0].booking_id' 2>/dev/null || echo "No bookings"
else
  echo "❌ Login failed"
fi
