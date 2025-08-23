FROM public.ecr.aws/lambda/python:3.13

ENV PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    CHROME_BIN=/opt/chrome/chrome \
    CHROMEDRIVER=/opt/chromedriver/chromedriver

# 필요한 런타임 라이브러리 + 유틸 + 폰트
RUN dnf -y update && \
    dnf -y install \
        unzip \
        ca-certificates \
        nss \
        atk \
        at-spi2-core \
        gtk3 \
        pango \
        libXcomposite \
        libXrandr \
        libXcursor \
        libXdamage \
        libXfixes \
        libXrender \
        libXi \
        libXScrnSaver \
        alsa-lib \
        cups-libs \
        libdrm \
        mesa-libgbm \
        dejavu-sans-fonts \
        liberation-fonts \
        fontconfig \
        wget && \
    dnf clean all && rm -rf /var/cache/dnf

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

# Lambda 환경에서 Chrome 실행을 위한 추가 설정
RUN mkdir -p /tmp/chrome && \
    chmod 777 /tmp/chrome && \
    mkdir -p /tmp/chromedriver && \
    chmod 777 /tmp/chromedriver && \
    mkdir -p /dev/shm && \
    chmod 777 /dev/shm && \
    mkdir -p /tmp/.X11-unix && \
    chmod 777 /tmp/.X11-unix && \
    mkdir -p /tmp/.org.chromium.Chromium.XXXXXX && \
    chmod 777 /tmp/.org.chromium.Chromium.XXXXXX

# Chrome sandbox 권한 설정
RUN chown -R root:root /opt/chrome && \
    chmod -R 755 /opt/chrome && \
    chmod 4755 /opt/chrome/chrome_sandbox

# 바이너리 버전 확인 (설치 검증용)
RUN /opt/chrome/chrome --version && /opt/chromedriver/chromedriver --version

# Python deps는 Lambda 작업 디렉토리에 설치
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# 소스 코드 복사 (모든 모듈 포함)
COPY app.py ${LAMBDA_TASK_ROOT}
COPY webdriver/ ${LAMBDA_TASK_ROOT}/webdriver/
COPY crawler/ ${LAMBDA_TASK_ROOT}/crawler/
COPY db/ ${LAMBDA_TASK_ROOT}/db/

# Lambda 핸들러
CMD ["app.handler"]
