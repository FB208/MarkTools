
from flask import current_app as app
import requests
import time
from datetime import datetime

class FAS5APIService:
    def __init__(self):
        self.token = app.config['FAS5_TOKEN']
        self.api_url = app.config['FAS5_API_URL']
        self.headers = {
            'token': f'{self.token}'
        }

    def get_org_trees(self):
        '''
        获取组织架构树
        '''
        url = f"{self.api_url}/api/v1/org-trees"
        response = requests.get(url, headers=self.headers)
        
        return response.json()
    
    def get_device_alarm_messages_type_count(self,createStartTime,createEndTime,type):
        '''
        获取设备告警消息类型统计
        createStartTime: 开始时间（yyyy-MM-dd）
        createEndTime: 结束时间（yyyy-MM-dd）
        type: 告警类型
        '''
        url = f"{self.api_url}/api/v1/device-alarm-messages/type-count"


        params = {
            "createStartTime": int(time.mktime(datetime.strptime(createStartTime, "%Y-%m-%d").timetuple())),
            "createEndTime": int(time.mktime(datetime.strptime(createEndTime, "%Y-%m-%d").timetuple())),
            "type": type
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
