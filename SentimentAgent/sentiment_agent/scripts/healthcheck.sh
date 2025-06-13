# scripts/healthcheck.sh

#!/bin/bash

# Basic health check script for Streamlit app

APP_PORT=8501
HOST=localhost

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$HOST:$APP_PORT/health)

if [ "$RESPONSE" -ne 200 ]; then
  echo "Healthcheck failed: $RESPONSE"
  exit 1
else
  echo "Healthcheck passed: $RESPONSE"
  exit 0
fi
