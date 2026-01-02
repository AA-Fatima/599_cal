#!/bin/bash

# Test script for backend_chatbot API endpoints
# This tests all endpoints using curl

BASE_URL="http://localhost:8001"

echo "========================================"
echo "Backend Chatbot API Endpoint Tests"
echo "========================================"

# Test 1: Health check
echo -e "\n1. Testing Health Check..."
curl -s "$BASE_URL/health" | python3 -m json.tool

# Test 2: Root endpoint
echo -e "\n2. Testing Root Endpoint..."
curl -s "$BASE_URL/" | python3 -m json.tool

# Test 3: Get all dishes
echo -e "\n3. Testing GET /api/dishes..."
curl -s "$BASE_URL/api/dishes" | python3 -m json.tool | head -30

# Test 4: Get specific dish
echo -e "\n4. Testing GET /api/dishes/{name}..."
curl -s "$BASE_URL/api/dishes/Chicken%20Shawarma%20Wrap" | python3 -m json.tool

# Test 5: USDA search
echo -e "\n5. Testing GET /api/usda/search?q=chicken..."
curl -s "$BASE_URL/api/usda/search?q=chicken" | python3 -m json.tool

# Test 6: Get missing dishes
echo -e "\n6. Testing GET /api/missing-dishes..."
curl -s "$BASE_URL/api/missing-dishes" | python3 -m json.tool

# Test 7: POST /api/chat (requires OpenAI key)
echo -e "\n7. Testing POST /api/chat (with fallback)..."
curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "chicken shawarma wrap"}' | python3 -m json.tool

echo -e "\n========================================"
echo "Tests completed!"
echo "========================================"
