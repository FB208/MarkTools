from google.cloud import storage
import base64

# 列出存储桶
def list_buckets():
    """Lists all buckets."""

    storage_client = storage.Client()
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)

# 上传文件
def upload_blob(bucket_name, file_path, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    generation_match_precondition = 0
    blob.upload_from_filename(file_path, if_generation_match=generation_match_precondition)
    return f"gs://{bucket_name}/{destination_blob_name}"