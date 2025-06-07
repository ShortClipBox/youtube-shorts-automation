#!/bin/bash

# 환경 변수 설정
PROJECT_ID="shortclipbox"
SERVICE_NAME="youtube-shorts-automation"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/${SERVICE_NAME}/app:latest"
REGION="us-central1"

# Cloud Run 서비스 배포
echo "Deploying Cloud Run service ${SERVICE_NAME} to region ${REGION}..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 1 \
  --timeout 300 \
  --project ${PROJECT_ID} \
  --quiet

echo "Cloud Run service deployed." 