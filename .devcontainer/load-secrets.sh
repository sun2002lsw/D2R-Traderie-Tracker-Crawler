#!/bin/bash

echo "=== load-secrets.sh 시작 ==="
echo "현재 디렉토리: $(pwd)"
echo "현재 사용자: $(whoami)"

# secrets.json 파일 경로 확인
SECRETS_FILE="/workspaces/D2R-Traderie-Tracker-Crawler/secrets.json"
echo "secrets.json 경로: ${SECRETS_FILE}"

# secrets.json 파일 존재 확인
if [ -f "${SECRETS_FILE}" ]; then
    echo "✓ secrets.json 파일 발견!"
    
    # 파일 내용 확인 (비밀번호는 숨김)
    echo "파일 내용:"
    cat "${SECRETS_FILE}"
    
    # jq 설치 확인 및 설치
    if ! command -v jq &> /dev/null; then
        echo "jq 설치 중..."
        apt-get update && apt-get install -y jq
    fi
    
    # 환경변수 설정
    export TRADERIE_ID=$(jq -r '.traderie_id' "${SECRETS_FILE}")
    export TRADERIE_PWD=$(jq -r '.traderie_pwd' "${SECRETS_FILE}")
    
    echo "환경변수 설정 완료:"
    echo "TRADERIE_ID: ${TRADERIE_ID}"
    echo "TRADERIE_PWD: ${TRADERIE_PWD}"
    
    # .bashrc에 추가
    echo "export TRADERIE_ID=${TRADERIE_ID}" >> ~/.bashrc
    echo "export TRADERIE_PWD=${TRADERIE_PWD}" >> ~/.bashrc
    
    echo "✓ .bashrc에 환경변수 추가 완료"
    echo "✓ Secrets 로드 성공!"
else
    echo "✗ secrets.json 파일을 찾을 수 없습니다!"
    echo "현재 디렉토리 내용:"
    ls -la /workspaces/D2R-Traderie-Tracker-Crawler/
    echo "상위 디렉토리 내용:"
    ls -la /workspaces/
fi

echo "=== load-secrets.sh 종료 ==="
