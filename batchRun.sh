#!/bin/bash

# 도커 컨테이너 이름 또는 ID
CONTAINER_NAME_OR_ID="your_container_name_or_id"

# 도커 컨테이너 내에서 monitoring.py 실행
docker exec $CONTAINER_NAME_OR_ID python3 /path/to/monitoring.py || true

echo "Script executed successfully!"
