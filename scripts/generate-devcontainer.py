#!/usr/bin/env python3
"""
Dev Container 설정 생성 스크립트
config.yaml의 설정을 devcontainer.json.template에 적용하여 devcontainer.json을 생성합니다.
로컬 개발 환경에서만 사용됩니다.
"""

import yaml
import os

def load_config():
    """config.yaml 파일을 로드합니다."""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_template():
    """devcontainer.json.template 파일을 로드합니다."""
    with open('.devcontainer/devcontainer.json.template', 'r', encoding='utf-8') as f:
        return f.read()

def generate_devcontainer(config, template):
    """템플릿에 설정을 적용하여 devcontainer.json을 생성합니다."""
    # 로컬 개발용 Python 이미지 사용 (안정적)
    python_image = f"python:{config['python_version']}-slim"
    
    # 템플릿 변수 치환
    devcontainer = template.replace('{{BASE_IMAGE}}', python_image)
    devcontainer = devcontainer.replace('{{CHROME_VERSION}}', config['chrome_version'])
    devcontainer = devcontainer.replace('{{CHROME_BIN}}', config['chrome_bin'])
    devcontainer = devcontainer.replace('{{CHROMEDRIVER_PATH}}', config['chromedriver_path'])
    
    return devcontainer

def main():
    """메인 함수"""
    try:
        # 설정 및 템플릿 로드
        config = load_config()
        template = load_template()
        
        # devcontainer.json 생성
        devcontainer_content = generate_devcontainer(config, template)
        
        # devcontainer.json 저장
        with open('.devcontainer/devcontainer.json', 'w', encoding='utf-8') as f:
            f.write(devcontainer_content)
        
        print("✅ Dev Container 설정 생성 완료!")
        print(f"   - 베이스 이미지: python:{config['python_version']}-slim (로컬 개발용)")
        print(f"   - Python 버전: {config['python_version']}")
        print(f"   - Chrome 버전: {config['chrome_version']}")
        print("   - .devcontainer/devcontainer.json 생성됨")
        
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()
