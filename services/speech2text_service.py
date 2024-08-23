import requests
import json
import os
import uuid
import base64
from werkzeug.utils import secure_filename
from flask import current_app as app
from utils.google_blob_util import upload_blob
from utils.google_speech_to_text_util import run_quickstart
def get_text(file):
    file_extension = os.path.splitext(secure_filename(file.filename))[1]
    blob_name = f"{uuid.uuid4()}{file_extension}"
    bucket_name = app.config['BUCKET_NAME']
    file_path = os.path.join('tempfiles', secure_filename(file.filename))
    file.save(file_path)
    # 上传文件到 Google Cloud Storage
    public_url = upload_blob(bucket_name, file_path, blob_name)
    os.remove(file_path)
    #text = run_quickstart(gcs_uri)
    return public_url