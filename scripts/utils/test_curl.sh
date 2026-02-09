#!/bin/bash
API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
echo "Testing API Key: ${API_KEY:0:10}..."

echo "--- Testing v1beta/models ---"
curl "https://generativelanguage.googleapis.com/v1beta/models?key=${API_KEY}" 

echo -e "\n\n--- Testing v1/models ---"
curl "https://generativelanguage.googleapis.com/v1/models?key=${API_KEY}"
