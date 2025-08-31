FROM python:3.13-slim

# Set environment variables
ENV PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    CHROME_BIN=/opt/chrome/chrome \
    CHROMEDRIVER=/opt/chromedriver/chromedriver

# 필요한 런타임 라이브러리 + 유틸 + 폰트
RUN apt-get update && \
    apt-get install -y \
        unzip \
        ca-certificates \
        wget \
        curl \
        gnupg \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxss1 \
        libxtst6 \
        xdg-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Chrome for Testing (stable) + chromedriver (stable) 다운로드/설치
RUN set -eux; \
    STABLE="$(python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'))['channels']['Stable']['version'])")"; \
    echo "Stable version: ${STABLE}"; \
    base="https://storage.googleapis.com/chrome-for-testing-public/${STABLE}/linux64"; \
    \
    # Chrome
    curl -fsSL "${base}/chrome-linux64.zip" -o /tmp/chrome.zip; \
    mkdir -p /opt/chrome; unzip -q /tmp/chrome.zip -d /opt; \
    mv /opt/chrome-linux64/* /opt/chrome/; \
    rm -rf /tmp/chrome.zip /opt/chrome-linux64; \
    \
    # Chromedriver
    curl -fsSL "${base}/chromedriver-linux64.zip" -o /tmp/chromedriver.zip; \
    mkdir -p /opt/chromedriver; unzip -q /tmp/chromedriver.zip -d /opt; \
    mv /opt/chromedriver-linux64/* /opt/chromedriver/; \
    rm -rf /tmp/chromedriver.zip /opt/chromedriver-linux64; \
    \
    # 실행 권한
    chmod +x /opt/chrome/chrome /opt/chromedriver/chromedriver

# Chrome 실행을 위한 디렉토리 설정
RUN mkdir -p /tmp/chrome && \
    chmod 777 /tmp/chrome && \
    mkdir -p /tmp/chromedriver && \
    chmod 777 /tmp/chromedriver && \
    mkdir -p /dev/shm && \
    chmod 777 /dev/shm && \
    mkdir -p /tmp/.X11-unix && \
    chmod 777 /tmp/.X11-unix

# Chrome sandbox 권한 설정
RUN chown -R root:root /opt/chrome && \
    chmod -R 755 /opt/chrome && \
    chmod 4755 /opt/chrome/chrome_sandbox

# 바이너리 버전 확인 (설치 검증용)
RUN /opt/chrome/chrome --version && /opt/chromedriver/chromedriver --version

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 코드 복사 (모든 모듈 포함)
COPY main.py .
COPY webdriver/ ./webdriver/
COPY traderie/ ./traderie/
COPY db/ ./db/
COPY helper/ ./helper/

# 컨테이너 실행 시 main.py 실행
CMD ["python", "main.py"]
