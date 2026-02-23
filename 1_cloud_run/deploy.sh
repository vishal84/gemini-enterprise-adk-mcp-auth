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
REPO_NAME="${REPO_NAME:-$SERVICE_NAME}"

# Validate that PROJECT_ID is set.
if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: PROJECT_ID is not set."
    echo "Please set the PROJECT_ID environment variable or run 'gcloud config set project YOUR_PROJECT_ID'."
    exit 1
fi

echo "🔧 Enabling required Google Cloud services (this may take a few minutes)..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    --project="${PROJECT_ID}"

echo "🔐 Granting necessary IAM roles for deployment..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Cloud Run Admin role to the Cloud Build SA to allow it to deploy
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/run.admin" \
    --condition=None > /dev/null

# Grant Service Account User role to the Cloud Build SA to allow it to act as the Cloud Run service's identity
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None > /dev/null

# Grant Cloud Run Admin role to the default Compute Engine SA
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/run.admin" \
    --condition=None > /dev/null

# Grant Service Account User role to the Compute Engine SA to allow it to act as the Cloud Run service's identity
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None > /dev/null

echo "🚀 Starting Cloud Build with the following configuration:"
echo "   Project: ${PROJECT_ID}"
echo "   Region: ${REGION}"
echo "   Repository: ${REPO_NAME}"
echo "   Service: ${SERVICE_NAME}"

echo "📦 Ensuring Artifact Registry repository '${REPO_NAME}' exists..."
if ! gcloud artifacts repositories describe "${REPO_NAME}" --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    echo "   Repository not found. Creating it now..."
    gcloud artifacts repositories create "${REPO_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="Docker repository for the ${SERVICE_NAME} service" \
        --project="${PROJECT_ID}"
fi

# Submit the build with substitutions
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --substitutions="_REGION=${REGION},_REPO_NAME=${REPO_NAME},_SERVICE_NAME=${SERVICE_NAME}"

echo "✅ Cloud Build completed successfully!"

echo "🔗 Fetching deployed service URL..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format="value(status.url)")

if [[ -n "$SERVICE_URL" ]]; then
    echo "🎉 Service is available at: ${SERVICE_URL}"
else
    echo "⚠️ Could not retrieve service URL. Please check the Cloud Run console."
fi
