import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api

B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APP_KEY = os.getenv("B2_APP_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

def upload_file_to_b2(file_bytes: bytes, file_name: str, content_type: str = None) -> str:
    """
    Uploads bytes to Backblaze B2 and returns a signed URL.
    """
    file_info = {}
    if content_type:
        file_info['Content-Type'] = content_type
    
    uploaded_file = bucket.upload_bytes(
        file_bytes,
        file_name,
        file_infos=file_info if file_info else None,
        content_type=content_type
    )
    
    return file_name

def get_download_authorization(file_name_prefix, valid_duration_seconds=3600):
    auth_token = bucket.get_download_authorization(
        file_name_prefix=file_name_prefix,
        valid_duration_in_seconds=valid_duration_seconds
    )
    return auth_token

def generate_download_url(file_path, auth_token):
    download_url = b2_api.get_download_url_for_file_name(
        bucket_name=B2_BUCKET_NAME,
        file_name=file_path
    )
    return f"{download_url}?Authorization={auth_token}"