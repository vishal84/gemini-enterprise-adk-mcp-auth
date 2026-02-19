#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-mcp-server}"
IMAGE_NAME="${IMAGE_NAME:-$SERVICE_NAME}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PLATFORM="managed"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"

if [[ -z "$PROJECT_ID" ]]; then
	echo "ERROR: PROJECT_ID is required."
	echo "Example: PROJECT_ID=my-gcp-project ./cloud_run/deploy.sh"
	exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
	echo "ERROR: gcloud CLI is not installed or not on PATH."
	exit 1
fi

IMAGE="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "==> Configuring gcloud project"
gcloud config set project "$PROJECT_ID"

echo "==> Enabling required services"
gcloud services enable \
	run.googleapis.com \
	cloudbuild.googleapis.com \
	artifactregistry.googleapis.com

echo "==> Building container image with Cloud Build"
gcloud builds submit --tag "$IMAGE" .

echo "==> Deploying service to Cloud Run"
DEPLOY_CMD=(
	gcloud run deploy "$SERVICE_NAME"
	--image "$IMAGE"
	--region "$REGION"
	--platform "$PLATFORM"
)

if [[ "$ALLOW_UNAUTHENTICATED" == "true" ]]; then
	DEPLOY_CMD+=(--allow-unauthenticated)
else
	DEPLOY_CMD+=(--no-allow-unauthenticated)
fi

"${DEPLOY_CMD[@]}"

SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')"

echo ""
echo "Deployment complete"
echo "Project:  $PROJECT_ID"
echo "Region:   $REGION"
echo "Service:  $SERVICE_NAME"
echo "Image:    $IMAGE"
echo "URL:      $SERVICE_URL"
