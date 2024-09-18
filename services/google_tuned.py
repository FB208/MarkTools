import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google.generativeai as genai
import os   

def list():
    # 使用服务账号 JSON 文件进行身份验证

    # credentials_path = os.path.abspath('/google_credentials/meta-buckeye-433400-c6-109fbeae7021.json')
    credentials, _ = google.auth.load_credentials_from_file("google_credentials/meta-buckeye-433400-c6-109fbeae7021.json")

    # 如果凭据需要刷新，刷新它
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # 配置 genai 使用这些凭据
    genai.configure(credentials=credentials)

    # 现在您可以使用 API 了
    for model_info in genai.list_tuned_models():
        print(model_info.name)