FROM --platform=linux/amd64 python:3.9-slim

# FFmpeg 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 및 디렉토리 복사
COPY requirements.txt .
COPY setup.py .
COPY pyproject.toml .
COPY src /app/src
COPY assets /app/assets
RUN mkdir -p /app/logs

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn[standard] && \
    pip install -e .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

# 실행 명령 (디버그 정보 유지)
CMD ["python", "-c", "import uvicorn, os; uvicorn.run(\"src.main:app\", host=\"0.0.0.0\", port=int(os.environ.get(\"PORT\", 8080)))"] 