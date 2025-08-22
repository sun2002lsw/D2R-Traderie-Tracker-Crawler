# D2R-Traderie-Tracker-Crawler
디아블로2 트레더리 추적기 크롤러

## 프로젝트 개요
이 프로젝트는 디아블로2 리저렉트의 트레더리 사이트에서 아이템 정보를 크롤링하는 AWS Lambda 함수입니다.

## 설정 파일 관리

### config.yaml
프로젝트의 공통 설정을 담고 있는 중앙 설정 파일입니다:
- 베이스 이미지 및 Python 버전
- Chrome 및 ChromeDriver 설정
- 시스템 패키지 목록
- Lambda 핸들러 설정

### 템플릿 기반 설정 생성
`config.yaml`의 값을 사용하여 다음 파일들을 자동 생성합니다:

1. **Dockerfile**: Docker 이미지 빌드를 위한 파일
2. **devcontainer.json**: VS Code Dev Container 설정 파일

### 설정 파일 생성 방법

```bash
# Dev Container 설정 생성 (로컬 개발용)
python scripts/generate-devcontainer.py

# Dockerfile 생성 (배포용)
python scripts/generate-dockerfile.py
```

## 개발 환경 설정

### 1. Dev Container 사용
1. VS Code에서 Dev Container 확장 설치
2. 프로젝트 폴더를 Dev Container로 열기
3. `config.yaml` 수정 후 `generate-devcontainer.py` 실행하여 설정 동기화

#### 2. Dev Container 환경 준비
Dev Container가 시작되면 자동으로 Python 환경이 준비됩니다:
- requirements.txt 자동 설치
- Python 버전 및 패키지 확인
- 개발 환경 준비 완료 메시지 표시

## 배포

### Docker 이미지 빌드
```bash
# Dockerfile 생성
python scripts/generate-dockerfile.py

# Docker 이미지 빌드
docker build -t d2r-crawler .
```

### AWS Lambda 배포
1. Docker 이미지를 ECR에 푸시
2. Lambda 함수 생성 및 이미지 연결
3. 환경 변수 설정 (필요시)

## 주의사항
- `config.yaml` 수정 후 용도에 맞는 스크립트를 실행하세요:
  - 로컬 개발: `generate-devcontainer.py`
  - 배포: `generate-dockerfile.py`
- Chrome 버전은 자동으로 최신 안정 버전을 감지합니다
- 시스템 패키지 목록은 Chrome 실행에 필요한 의존성들을 포함합니다
