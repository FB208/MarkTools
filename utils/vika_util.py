import requests
from flask import current_app as app
class VikaClient:
    def __init__(self):
        self.api_token = app.config['VIKA_API_TOKEN']
        self.space_id = app.config['VIKA_SPACE_ID']

    # 创建数据表
    def create_datasheet(self, name, description="", folder_id=None, pre_node_id=None, fields=None):
        url = f"https://vika.cn/fusion/v1/spaces/{self.space_id}/datasheets"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "name": name,
            "description": description,
            "folderId": folder_id,
            "preNodeId": pre_node_id,
            "fields": fields if fields else []
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            
    