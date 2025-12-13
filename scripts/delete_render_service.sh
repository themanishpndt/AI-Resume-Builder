#!/usr/bin/env bash
# Safely delete a Render service using the Render API.
# Usage:
#   export RENDER_API_KEY="your_api_key"
#   ./scripts/delete_render_service.sh --service-name my-service
#
# This script will list services, try to find a matching name (case-sensitive) and
# delete the first match after asking for confirmation. It requires curl and jq.

set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required. Install it and re-run."
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required for JSON parsing. Install it (e.g. apt install jq) and re-run."
  exit 2
fi

if [ -z "${RENDER_API_KEY:-}" ]; then
  echo "Please set RENDER_API_KEY environment variable with a Render API key."
  exit 2
fi

SERVICE_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --service-name) SERVICE_NAME="$2"; shift 2;;
    --service-id) SERVICE_ID="$2"; shift 2;;
    -h|--help) echo "Usage: $0 --service-name NAME [--service-id ID]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ -z "${SERVICE_NAME:-}" ] && [ -z "${SERVICE_ID:-}" ]; then
  echo "Provide --service-name or --service-id to identify the service to delete."
  exit 1
fi

API_BASE="https://api.render.com/v1"

if [ -n "${SERVICE_ID:-}" ]; then
  TARGET_ID="$SERVICE_ID"
else
  echo "Looking up services for name: $SERVICE_NAME"
  SERVICES_JSON=$(curl -sS -H "Authorization: Bearer $RENDER_API_KEY" "$API_BASE/services")
  TARGET_ID=$(echo "$SERVICES_JSON" | jq -r --arg NAME "$SERVICE_NAME" '.[] | select(.name == $NAME) | .id' | head -n1 || true)
  if [ -z "$TARGET_ID" ]; then
    echo "No service with name '$SERVICE_NAME' found. Available services:"
    echo "$SERVICES_JSON" | jq -r '.[] | "- " + .name + " (" + .id + ")"'
    exit 1
  fi
fi

echo "Found service id: $TARGET_ID"
read -p "Are you sure you want to DELETE this Render service? This is irreversible. (yes/no) " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborting. No changes made."
  exit 0
fi

echo "Deleting service $TARGET_ID..."
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X DELETE -H "Authorization: Bearer $RENDER_API_KEY" "$API_BASE/services/$TARGET_ID")
if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  echo "Service deleted (HTTP $HTTP_CODE)."
else
  echo "Failed to delete service. HTTP status: $HTTP_CODE"
  echo "You can inspect the delete call response by running the curl command manually with the same headers."
  exit 1
fi

echo "Done."
