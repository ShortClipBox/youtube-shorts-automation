#!/bin/bash

# 환경 변수 설정
PROJECT_ID="shortclipbox"  # GCP 프로젝트 ID
REGION="asia-northeast3"      # 서울 리전
SERVICE_NAME="youtube-shorts-automation"
SCHEDULE="0 */6 * * *"       # 6시간마다 실행

# Cloud Scheduler 작업 생성
gcloud scheduler jobs create http youtube-shorts-automation-job \
  --schedule="$SCHEDULE" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/services/$SERVICE_NAME:run" \
  --http-method=POST \
  --oauth-service-account-email="$PROJECT_ID@appspot.gserviceaccount.com" \
  --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform" 