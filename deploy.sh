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
  --set-env-vars="TZ=Asia/Seoul,REDIRECT_URI=https://youtube-shorts-automation-381688299677.us-central1.run.app/auth/callback" \
  --set-secrets="YOUTUBE_CLIENT_ID=YOUTUBE_CLIENT_ID:latest,YOUTUBE_CLIENT_SECRET=YOUTUBE_CLIENT_SECRET:latest,YOUTUBE_API_KEY=YOUTUBE_API_KEY:latest" \
  --quiet

echo "Cloud Run service deployed." 