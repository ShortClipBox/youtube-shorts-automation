#!/bin/bash

# 환경 변수 설정
PROJECT_ID="shortclipbox"
SERVICE_NAME="youtube-shorts-automation"
REGION="us-central1"
JOB_NAME="run-youtube-shorts-automation"
SCHEDULE="0 0 * * *" # 매일 자정 실행

# Cloud Scheduler 작업 생성
echo "Creating Cloud Scheduler job ${JOB_NAME}..."
gcloud scheduler jobs create http ${JOB_NAME} \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="${SCHEDULE}" \
  --uri="https://${SERVICE_NAME}-381688299677.${REGION}.run.app" \
  --http-method=POST \
  --message-body='{}' \
  --time-zone="Asia/Seoul" \
  --oidc-service-account-email="381688299677-compute@developer.gserviceaccount.com"

echo "Cloud Scheduler job ${JOB_NAME} created." 