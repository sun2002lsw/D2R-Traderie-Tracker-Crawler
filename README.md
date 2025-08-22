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

### Dev Container 사용
1. VS Code에서 Dev Container 확장 설치
2. 프로젝트 폴더를 Dev Container로 열기
3. `config.yaml` 수정 후 `generate-devcontainer.py` 실행하여 설정 동기화

#### Dev Container 문제 해결
Dev Container 설정을 변경한 후 문제가 발생하면 정리 스크립트를 사용하세요:

##### 방법 1: VS Code Task (권장)
1. **`Ctrl+Shift+P`** → **"Tasks: Run Task"**
2. **"Dev Container 정리 및 재시작"** 선택
3. 자동으로 정리 완료 후 새 컨테이너 시작

##### 방법 2: 단축키
- **`Ctrl+Shift+D`**: Dev Container 정리 및 재시작
- **`Ctrl+Shift+G`**: Dev Container 설정 생성
- **`Ctrl+Shift+F`**: Dockerfile 생성

##### 방법 3: 터미널
```bash
# Dev Container 완전 정리 및 재시작
python scripts/clean-devcontainer.py
```

이 스크립트는:
- 기존 Dev Container 컨테이너를 완전히 삭제
- 사용하지 않는 Docker 이미지 정리
- 새 컨테이너에서 깨끗하게 시작할 수 있도록 도움

### 로컬 개발
```bash
pip install -r requirements.txt
python app.py
```

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
