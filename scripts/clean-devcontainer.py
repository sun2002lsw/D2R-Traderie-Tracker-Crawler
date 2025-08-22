#!/usr/bin/env python3
"""
Dev Container 정리 및 재시작 스크립트
기존 컨테이너를 완전히 삭제하고 새로 시작할 수 있도록 도와줍니다.
"""

import subprocess
import json
import os
import sys

def run_command(command, check=True):
    """명령어를 실행하고 결과를 반환합니다."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ 명령어 실행 실패: {command}")
            print(f"   오류: {result.stderr}")
            return False
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ 명령어 실행 중 오류: {e}")
        return False

def get_devcontainer_containers():
    """Dev Container 관련 컨테이너들을 찾습니다."""
    try:
        # 모든 컨테이너를 가져와서 Dev Container 관련 컨테이너 찾기
        result = subprocess.run(
            'docker ps -a --format "{{.ID}}:{{.Names}}:{{.Status}}:{{.Image}}"',
            shell=True, capture_output=True, text=True
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split(':')
                if len(parts) >= 4:
                    # Dev Container 관련 컨테이너인지 확인
                    # 1. 이미지가 config.yaml의 base_image와 일치하거나
                    # 2. 이름이 devcontainer 관련 패턴과 일치하는 경우
                    image = parts[3]
                    name = parts[1]
                    
                    # AWS Lambda Python 이미지 또는 devcontainer 관련 이름인 경우
                    if ("public.ecr.aws/lambda/python" in image or 
                        "devcontainer" in name.lower() or
                        any(keyword in name.lower() for keyword in ["vsc", "cursor", "dev"])):
                        containers.append({
                            'id': parts[0],
                            'name': parts[1],
                            'status': parts[2],
                            'image': parts[3]
                        })
        
        return containers
    except Exception as e:
        print(f"❌ 컨테이너 목록 조회 실패: {e}")
        return []

def stop_and_remove_containers(containers):
    """컨테이너들을 중지하고 삭제합니다."""
    if not containers:
        print("ℹ️  삭제할 Dev Container가 없습니다.")
        return True
    
    print(f"🔄 {len(containers)}개의 Dev Container를 정리합니다...")
    
    for container in containers:
        container_id = container['id']
        container_name = container['name']
        container_status = container['status']
        
        print(f"   - {container_name} ({container_id}) - {container_status}")
        print(f"     이미지: {container['image']}")
        
        # 컨테이너 중지
        if "Up" in container_status:
            print(f"     중지 중...")
            if not run_command(f"docker stop {container_id}", check=False):
                print(f"     ⚠️  중지 실패, 강제 삭제 시도...")
        
        # 컨테이너 삭제
        print(f"     삭제 중...")
        if not run_command(f"docker rm {container_id}", check=False):
            print(f"     ❌ 삭제 실패")
        else:
            print(f"     ✅ 삭제 완료")
    
    return True

def clean_docker_images():
    """사용하지 않는 Docker 이미지들을 정리합니다."""
    print("🧹 사용하지 않는 Docker 이미지 정리 중...")
    
    # dangling 이미지 삭제
    result = run_command("docker images -f 'dangling=true' -q", check=False)
    if result:
        dangling_images = result.split('\n')
        if dangling_images and dangling_images[0]:
            print(f"   - {len(dangling_images)}개의 dangling 이미지 삭제 중...")
            run_command("docker rmi $(docker images -f 'dangling=true' -q)", check=False)
    
    # 사용하지 않는 이미지 삭제
    print("   - 사용하지 않는 이미지 정리 중...")
    run_command("docker image prune -f", check=False)

def main():
    """메인 함수"""
    print("🚀 Dev Container 정리 및 재시작 스크립트")
    print("=" * 50)
    
    # 1. Dev Container 컨테이너 찾기
    print("1️⃣ Dev Container 컨테이너 검색 중...")
    containers = get_devcontainer_containers()
    
    if containers:
        print(f"   📋 발견된 컨테이너: {len(containers)}개")
        for container in containers:
            print(f"      - {container['name']} ({container['id']}) - {container['status']}")
            print(f"        이미지: {container['image']}")
    else:
        print("   ℹ️  실행 중인 Dev Container가 없습니다.")
    
    # 2. 컨테이너 정리
    print("\n2️⃣ 컨테이너 정리 중...")
    if not stop_and_remove_containers(containers):
        print("❌ 컨테이너 정리 실패")
        return
    
    # 3. Docker 이미지 정리
    print("\n3️⃣ Docker 이미지 정리 중...")
    clean_docker_images()
    
    # 4. 완료 메시지
    print("\n✅ Dev Container 정리 완료!")
    print("\n📋 다음 단계:")
    print("   1. VS Code에서 'Ctrl+Shift+P'")
    print("   2. 'Dev Containers: Open Folder in Container' 선택")
    print("   3. 프로젝트 폴더 선택")
    print("   4. 새 컨테이너에서 시작!")
    
    print("\n💡 팁: 이 스크립트를 매번 실행할 필요는 없습니다.")
    print("   Dev Container 설정을 변경한 후에만 실행하면 됩니다.")

if __name__ == "__main__":
    main()
