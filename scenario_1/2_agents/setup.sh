#!/usr/bin/env bash
set -euo pipefail

# Get the project ID from the gcloud configuration.
PROJECT_ID=$(gcloud config get-value project)

# Check if the project ID is set.
if [[ -z "$PROJECT_ID" ]]; then
    echo "Error: gcloud project not set. Please run 'gcloud config set project YOUR_PROJECT_ID'" >&2
    exit 1
fi

# Get the project number, which is needed to construct the service account email.
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")

# The service account to create
SA_NAME="code-snippet-sa"
SERVICE_IDENTITY_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create the service account if it doesn't exist
if ! gcloud iam service-accounts describe "${SERVICE_IDENTITY_EMAIL}" --project "${PROJECT_ID}" &> /dev/null; then
    echo "🤖 Creating service account ${SERVICE_IDENTITY_EMAIL}..."
    gcloud iam service-accounts create "${SA_NAME}" \
        --display-name="Agent Engine Service Account" \
        --project="${PROJECT_ID}" \
        --condition=None > /dev/null
else
    echo "✅ Service account ${SERVICE_IDENTITY_EMAIL} already exists."
fi

# Grant Cloud Run Invoker role
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_IDENTITY_EMAIL}" \
    --role="roles/run.invoker" \
    --condition=None > /dev/null

# Grant Logs Writer role
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_IDENTITY_EMAIL}" \
    --role="roles/logging.logWriter" \
    --condition=None > /dev/null

echo "✅ Roles granted successfully."

# Create a staging bucket for agent engine deployments
STAGING_BUCKET="agent-staging-${PROJECT_ID}"
if ! gcloud storage buckets describe "gs://${STAGING_BUCKET}" &> /dev/null; then
    echo "🤖 Creating staging bucket gs://${STAGING_BUCKET}..."
    gcloud storage buckets create "gs://${STAGING_BUCKET}" --project="${PROJECT_ID}" --location=US-CENTRAL1
else
    echo "✅ Staging bucket gs://${STAGING_BUCKET} already exists."
fi

echo "STAGING_BUCKET=${STAGING_BUCKET}"
