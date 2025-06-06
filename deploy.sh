#!/bin/bash

# 환경 변수 설정
PROJECT_ID="shortclipbox"  # GCP 프로젝트 ID
REGION="asia-northeast3"      # 서울 리전
SERVICE_NAME="youtube-shorts-automation"

# Docker 이미지 빌드
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# GCR에 이미지 푸시
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Cloud Run 서비스 배포
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 3600 \
  --set-env-vars="YOUTUBE_API_KEY=your-api-key"  # YouTube API 키 설정 