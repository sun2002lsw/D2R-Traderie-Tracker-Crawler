#!/bin/bash

# 에러 발생 시 즉시 종료
set -e

echo "=== load-secrets.sh 시작 ==="
echo "현재 디렉토리: $(pwd)"
echo "현재 사용자: $(whoami)"
echo "현재 시간: $(date)"

# secrets.json 파일 경로 확인
SECRETS_FILE="/workspaces/D2R-Traderie-Tracker-Crawler/secrets.json"
echo "secrets.json 경로: ${SECRETS_FILE}"

# secrets.json 파일 존재 확인
if [ -f "${SECRETS_FILE}" ]; then
    echo "✓ secrets.json 파일 발견!"
    
    # 파일 권한 확인
    echo "파일 권한: $(ls -la ${SECRETS_FILE})"
    
    # 파일 내용 확인 (비밀번호는 숨김)
    echo "파일 내용:"
    cat "${SECRETS_FILE}"
    
    # jq 설치 확인 및 설치
    if ! command -v jq &> /dev/null; then
        echo "jq 설치 중..."
        apt-get update && apt-get install -y jq
        echo "jq 설치 완료: $(jq --version)"
    else
        echo "✓ jq 이미 설치됨: $(jq --version)"
    fi
    
    # JSON 파싱 테스트
    echo "JSON 파싱 테스트 중..."
    if jq empty "${SECRETS_FILE}" 2>/dev/null; then
        echo "✓ JSON 형식 유효"
    else
        echo "✗ JSON 형식이 유효하지 않습니다!"
        exit 1
    fi
    
    # 환경변수 설정
    echo "환경변수 설정 중..."
    
    # Traderie 자격 증명 설정
    export TRADERIE_ID=$(jq -r '.TRADERIE_ID' "${SECRETS_FILE}")
    export TRADERIE_PWD=$(jq -r '.TRADERIE_PWD' "${SECRETS_FILE}")
    
    # Traderie 자격 증명 값 확인
    if [ -z "${TRADERIE_ID}" ] || [ "${TRADERIE_ID}" = "null" ]; then
        echo "✗ TRADERIE_ID가 설정되지 않았습니다!"
        exit 1
    fi
    
    if [ -z "${TRADERIE_PWD}" ] || [ "${TRADERIE_PWD}" = "null" ]; then
        echo "✗ TRADERIE_PWD가 설정되지 않았습니다!"
        exit 1
    fi
    
    echo "Traderie 자격 증명 설정 완료:"
    echo "TRADERIE_ID: ${TRADERIE_ID}"
    echo "TRADERIE_PWD: ${TRADERIE_PWD}"
    
    # .bashrc에 추가
    echo ".bashrc에 환경변수 추가 중..."
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
    echo "secrets.json 파일 검색 중..."
    find /workspaces -name "secrets.json" 2>/dev/null || echo "secrets.json 파일을 찾을 수 없습니다."
    exit 1
fi

echo "=== load-secrets.sh 종료 ==="
