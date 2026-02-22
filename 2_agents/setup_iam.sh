#!/usr/bin/env bash
set -euo pipefail

# Get the project ID from the gcloud configuration.
PROJECT_ID=$(gcloud config get-value project)

# Check if the project ID is set.
if [[ -z "$PROJECT_ID" ]]; then
    echo "Error: gcloud project not set. Please run 'gcloud config set project YOUR_PROJECT_ID'" >&2
    exit 1
fi

echo "🤖 Ensuring AI Platform service identity exists for project ${PROJECT_ID}..."

# This command is idempotent. It creates the service identity if it doesn't exist
# or ensures it's enabled if it does. We pipe the output to /dev/null
# as we will construct the email address ourselves in the next step.
gcloud beta services identity create --service=aiplatform.googleapis.com --project="${PROJECT_ID}" >/dev/null

# Get the project number, which is needed to construct the service account email.
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")

# The service identity email format is predictable.
SERVICE_IDENTITY_EMAIL="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"

echo "🤖 AI Platform service identity email: ${SERVICE_IDENTITY_EMAIL}"

echo "🤖 Granting additional roles to the default Agent Engine service account..."

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

 PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
 
 # The service identity email format is predictable.
SERVICE_IDENTITY_EMAIL="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
echo "🤖 Default Agent Engine service account email: ${SERVICE_IDENTITY_EMAIL}"
echo "✅ Roles granted successfully."

# Prompt for user's email
read -rp "Enter your email address to grant Service Account Token Creator role: " USER_EMAIL

if [[ -n "$USER_EMAIL" ]]; then
    echo "🤖 Granting Service Account Token Creator role to ${USER_EMAIL}..."
    gcloud iam service-accounts add-iam-policy-binding "${SERVICE_IDENTITY_EMAIL}" \
        --member="user:${USER_EMAIL}" \
        --role="roles/iam.serviceAccountTokenCreator" \
        --project="${PROJECT_ID}" > /dev/null
    echo "✅ ${USER_EMAIL} can now mint tokens for ${SERVICE_IDENTITY_EMAIL}."
else
    echo "⚠️ No email address provided. Skipping token creator role."
fi

