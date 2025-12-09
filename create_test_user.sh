#!/bin/bash
# Create a test user account

echo "📝 Creating test user account..."

# Create JSON data
USER_DATA='{
  "user_id": "888-44-3333",
  "first_name": "Sujith",
  "last_name": "Dugyala",
  "email": "sujith@gmail.com",
  "password": "test123",
  "phone_number": "555-0199",
  "address": "123 Main Street",
  "city": "San Jose",
  "state": "CA",
  "zip_code": "95123"
}'

RESPONSE=$(curl -s -X POST "http://localhost:8001/users" \
  -F "user_data=$USER_DATA")

echo "$RESPONSE" | jq '.'

if echo "$RESPONSE" | jq -e '.user_id' > /dev/null 2>&1; then
  echo ""
  echo "✅ User created successfully!"
  echo ""
  echo "🔑 Now testing login..."
  
  LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8001/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "sujith@gmail.com",
      "password": "test123"
    }')
  
  TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
  USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.user_id')
  
  if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "✅ Login successful!"
    echo "User ID: $USER_ID"
    echo ""
    echo "📊 Testing Profile API..."
    curl -s -X GET "http://localhost:8001/users/$USER_ID" \
      -H "Authorization: Bearer $TOKEN" | jq '.first_name, .last_name, .email'
  else
    echo "❌ Login failed"
    echo "$LOGIN_RESPONSE" | jq '.'
  fi
else
  echo "❌ User creation failed or user already exists"
  echo ""
  echo "Trying to login with existing user..."
  LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8001/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "sujith@gmail.com",
      "password": "test123"
    }')
  
  TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
  
  if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "✅ Existing user login successful!"
  else
    echo "❌ Login also failed"
  fi
fi
