#!/bin/bash
# Create a test admin account

echo "📝 Creating test admin account..."

# Create JSON data
ADMIN_DATA='{
  "admin_id": "ADMIN-TEST-001",
  "first_name": "Test",
  "last_name": "Admin",
  "email": "test.admin@kayak.com",
  "password": "testadmin123",
  "phone_number": "555-0100",
  "role": "admin"
}'

RESPONSE=$(curl -s -X POST "http://localhost:8006/auth/signup" \
  -F "admin_data=$ADMIN_DATA")

echo "$RESPONSE" | jq '.'

if echo "$RESPONSE" | jq -e '.admin' > /dev/null 2>&1; then
  echo ""
  echo "✅ Admin created successfully!"
  echo ""
  echo "🔑 Now testing login..."
  
  LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8006/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test.admin@kayak.com",
      "password": "testadmin123"
    }')
  
  TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
  
  if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "✅ Login successful!"
    echo ""
    echo "📊 Testing Dashboard Stats..."
    curl -s -X GET "http://localhost:8006/dashboard/stats" \
      -H "Authorization: Bearer $TOKEN" | jq '.'
  else
    echo "❌ Login failed"
    echo "$LOGIN_RESPONSE" | jq '.'
  fi
else
  echo "❌ Admin creation failed or admin already exists"
fi
