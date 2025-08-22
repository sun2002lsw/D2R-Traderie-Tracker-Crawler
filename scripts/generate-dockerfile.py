#!/usr/bin/env python3
"""
Dockerfile 생성 스크립트
config.yaml의 설정을 Dockerfile.template에 적용하여 Dockerfile을 생성합니다.
"""

import yaml
import os

def load_config():
    """config.yaml 파일을 로드합니다."""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_template():
    """Dockerfile.template 파일을 로드합니다."""
    with open('Dockerfile.template', 'r', encoding='utf-8') as f:
        return f.read()

def generate_dockerfile(config, template):
    """템플릿에 설정을 적용하여 Dockerfile을 생성합니다."""
    # 시스템 패키지들을 공백으로 구분된 문자열로 변환
    system_packages = ' '.join(config['system_packages'])
    
    # AWS Lambda Python 3.13 이미지 사용 (배포용)
    lambda_image = f"public.ecr.aws/lambda/python:{config['python_version']}"
    
    # 템플릿 변수 치환
    dockerfile = template.replace('{{BASE_IMAGE}}', lambda_image)
    dockerfile = dockerfile.replace('{{CHROME_BIN}}', config['chrome_bin'])
    dockerfile = dockerfile.replace('{{CHROMEDRIVER_PATH}}', config['chromedriver_path'])
    dockerfile = dockerfile.replace('{{CHROME_VERSION}}', config['chrome_version'])
    dockerfile = dockerfile.replace('{{LAMBDA_HANDLER}}', config['lambda_handler'])
    dockerfile = dockerfile.replace('{{SYSTEM_PACKAGES}}', system_packages)
    
    return dockerfile

def main():
    """메인 함수"""
    try:
        # 설정 및 템플릿 로드
        config = load_config()
        template = load_template()
        
        # AWS Lambda Python 3.13 이미지 사용 (배포용)
        lambda_image = f"public.ecr.aws/lambda/python:{config['python_version']}"
        
        # Dockerfile 생성
        dockerfile_content = generate_dockerfile(config, template)
        
        # Dockerfile 저장
        with open('Dockerfile', 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        print("✅ Dockerfile 생성 완료!")
        print(f"   - 베이스 이미지: {lambda_image}")
        print(f"   - Python 버전: {config['python_version']}")
        print(f"   - Chrome 버전: {config['chrome_version']}")
        
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()
