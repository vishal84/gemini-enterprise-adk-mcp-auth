#!/usr/bin/env bash
set -euo pipefail

# Load environment variables from .env file, if it exists.
if [ -f .env ]; then
    # Use set -a to export all variables defined in .env.
    set -a
    source .env
    # Use set +a to stop exporting variables.
    set +a
fi

# Function to check if a command exists.
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for gcloud CLI.
if ! command_exists gcloud; then
    echo "ERROR: gcloud CLI is not installed or not on PATH."
    exit 1
fi

# Set default values for environment variables.
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-code-snippet-mcp-server}"
REPOSITORY_NAME="${REPOSITORY_NAME:-$SERVICE_NAME}"
IMAGE_NAME="${IMAGE_NAME:-$SERVICE_NAME}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"

# Validate that PROJECT_ID is set.
if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: PROJECT_ID is not set."
    echo "Please set the PROJECT_ID environment variable or run 'gcloud config set project YOUR_PROJECT_ID'."
    exit 1
fi

# Define the image path for Artifact Registry.
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "==> Enabling required services"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com

# Grant the Cloud Build service account access to the GCS bucket.
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
GCE_SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "==> Granting Cloud Build permissions to access source"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${GCE_SERVICE_ACCOUNT}" \
    --role="roles/storage.objectViewer" --condition=None

# Create the Artifact Registry repository if it doesn't exist.
if ! gcloud artifacts repositories describe "$REPOSITORY_NAME" --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "==> Creating Artifact Registry repository: $REPOSITORY_NAME"
    gcloud artifacts repositories create "$REPOSITORY_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for $SERVICE_NAME"
fi

echo "==> Building container image with Cloud Build"
gcloud builds submit --tag "$IMAGE" .

echo "==> Deploying service to Cloud Run"
DEPLOY_CMD=(
    gcloud run deploy "$SERVICE_NAME"
    --image "$IMAGE"
    --region "$REGION"
    --platform "managed"
)

if [[ "$ALLOW_UNAUTHENTICATED" == "true" ]]; then
    DEPLOY_CMD+=(--allow-unauthenticated)
else
    DEPLOY_CMD+=(--no-allow-unauthenticated)
fi

# Execute the deployment command.
"${DEPLOY_CMD[@]}"

# Get the service URL.
SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')"

# Print deployment summary.
echo ""
echo "Deployment complete"
echo "Project:  $PROJECT_ID"
echo "Region:   $REGION"
echo "Service:  $SERVICE_NAME"
echo "Image:    $IMAGE"
echo "URL:      $SERVICE_URL"
