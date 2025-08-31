import os
from google.cloud import secretmanager


def get_traderie_credentials():
    traderie_id = os.environ.get("TRADERIE_ID")
    traderie_pwd = os.environ.get("TRADERIE_PWD")
    
    if not traderie_id or not traderie_pwd:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT 환경변수가 설정되지 않았습니다")
            
        if not traderie_id:
            traderie_id = _get_gcp_secret(project_id, "TRADERIE_ID")
        if not traderie_pwd:
            traderie_pwd = _get_gcp_secret(project_id, "TRADERIE_PWD")
    
    return traderie_id, traderie_pwd


# google cloud secret manager를 사용하여 비밀번호 가져오기
def _get_gcp_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
