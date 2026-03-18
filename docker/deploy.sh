#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

ENV_FILE="../.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: $ENV_FILE not found. Copy .env.example and fill in values."
  exit 1
fi

# Source env file
set -a
source "$ENV_FILE"
set +a

echo "==> Building Docker images..."
docker compose -f docker-compose.yml build

echo ""
echo "==> Creating/updating Docker secrets..."
for secret in notion_api_key notion_database_id notion_data_source_id notion_pages_data_source_id cache_invalidate_secret; do
  # Convert to uppercase env var name
  env_var=$(echo "$secret" | tr '[:lower:]' '[:upper:]')
  value="${!env_var:-}"

  if [ -z "$value" ]; then
    echo "Warning: $env_var is empty, skipping secret $secret"
    continue
  fi

  # Remove existing secret if it exists (secrets are immutable)
  docker secret rm "$secret" 2>/dev/null || true
  echo "$value" | docker secret create "$secret" -
  echo "  Created secret: $secret"
done

echo ""
echo "==> Deploying blog stack to Docker Swarm..."
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml blog

echo ""
echo "Done. Check status with:"
echo "  docker stack services blog"
echo "  docker stack ps blog"
