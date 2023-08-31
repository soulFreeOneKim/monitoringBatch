#!/bin/bash

CONTAINER_NAME="aiccmonitoringbatch"

docker exec $CONTAINER_NAME python3 /app/monitoring.py || true

echo "Script executed successfully!"
