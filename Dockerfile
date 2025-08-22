FROM python:3.13-slim

ENV PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    CHROME_BIN=/opt/chrome/chrome \
    CHROMEDRIVER=/opt/chromedriver/chromedriver

# 필요한 런타임 라이브러리 + 유틸 + 폰트
RUN apt-get update && \
    apt-get install -y \
        unzip \
        ca-certificates \
        nss \
        atk \
        at-spi2-core \
        gtk3 \
        pango \
        libxcomposite1 \
        libxrandr2 \
        libxcursor1 \
        libxdamage1 \
        libxfixes3 \
        libxrender1 \
        libxi6 \
        libxss1 \
        libasound2 \
        libcups2 \
        libdrm2 \
        libgbm1 \
        fonts-dejavu-core \
        fonts-liberation \
        fontconfig \
        wget \
        curl \
        gnupg2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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

# 바이너리 버전 확인 (설치 검증용)
RUN /opt/chrome/chrome --version && /opt/chromedriver/chromedriver --version

# Python deps 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 배치
COPY app.py .

# 실행 명령
CMD ["python", "app.py"]
