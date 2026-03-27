#!/usr/bin/env bash
# Manual / emergency deploy script.
# Normal production deploys are handled by the CI/CD pipeline (.github/workflows/deploy.yml).
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

echo "==> Creating/updating Docker secrets..."
for secret in notion_api_key notion_database_id notion_data_source_id notion_pages_data_source_id cache_invalidate_secret redis_password; do
  # Convert to uppercase env var name
  env_var=$(echo "$secret" | tr '[:lower:]' '[:upper:]')
  value="${!env_var:-}"

  if [ -z "$value" ]; then
    echo "Warning: $env_var is empty, skipping secret techblog_$secret"
    continue
  fi

  # Remove existing secret if it exists (secrets are immutable)
  docker secret rm "techblog_$secret" 2>/dev/null || true
  echo "$value" | docker secret create "techblog_$secret" -
  echo "  Created secret: techblog_$secret"
done

echo ""
echo "==> Deploying techblog stack to Docker Swarm..."
docker stack deploy --with-registry-auth -c docker-compose.yml -c docker-compose.prod.yml techblog

echo ""
echo "Done. Check status with:"
echo "  docker stack services techblog"
echo "  docker stack ps techblog"
