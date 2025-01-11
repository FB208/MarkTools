from flask import current_app as app
import requests
from utils.redis_util import RedisUtil

class StarBotAPIService:
    def __init__(self):
        self.token = app.config['STARBOT_TOKEN']
        self.api_url = app.config['STARBOT_API_URL']
        self.main_robot_id = app.config['STARBOT_MAIN_ROBOT_ID']
        self.headers = {
            'Authorization': f'{self.token}'
        }
        self.redis_util = RedisUtil()
        
    def get_account_list(self):
        '''
        获取登录账号信息，初次使用必须调用
        '''
        data = {
            "type": "getAccountListRequest",
            "params": {
                "status": 1
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=data)
        
        self.redis_util.array_add_or_replace('starbot:account_list', response.json().get('data'))
        return response.json()

    def get_robot_info(self):
        '''
        获取机器人信息获取已登录机器人信息
        '''
        account_list = self.redis_util.array_get_all('starbot:account_list')
        for account in account_list:
            data = {
                "type": "robotInfo",
                "params": {
                    "instanceId": account.get('instanceId'),
                    "cache": 1
                }
            }
            response = requests.post(self.api_url, headers=self.headers, json=data)
            self.redis_util.delete_by_pattern_scan(f'starbot:robot_info:*')
            self.redis_util.set_json(f'starbot:robot_info:{account.get("instanceId")}', response.json().get('data'))
        return response.json()
    
    def get_group_list(self):
        '''
        获取群聊信息
        '''
        account_list = self.redis_util.array_get_all('starbot:account_list')
        for account in account_list:
            data = {
                "type": "getGroupList",
                "params": {
                    "instanceId": account.get('instanceId'),
                    "cache": 0
                }
            }
            robot_info = self.redis_util.get_json(f'starbot:robot_info:{account.get("instanceId")}')
            response = requests.post(self.api_url, headers=self.headers, json=data)
            self.redis_util.array_add_or_replace(f'starbot:group_list:robotId_{robot_info.get("robotId")}', response.json().get('data'))
        return response.json()

    def get_friend_list(self):
        '''
        获取好友信息
        '''
        account_list = self.redis_util.array_get_all('starbot:account_list')
        for account in account_list:
            data = {
                "type": "getFriendList",
                "params": {
                    "instanceId": account.get('instanceId'),
                    "cache": 0
                }
            }
            response = requests.post(self.api_url, headers=self.headers, json=data)
            self.redis_util.array_add_or_replace(f'starbot:friend_list:robotId_{account.get("instanceId")}', response.json().get('data'))
        return response.json()

    def query_friend_or_group_info(self, wxId):
        '''
        获取好友或群聊详细信息
        '''
        account_list = self.redis_util.array_get_all('starbot:account_list')
        for account in account_list:
            data = {
                "type": "queryFriendOrGroupInfo",
                "params": {
                    "instanceId": account.get('instanceId'),
                    "wxId": wxId
                }
            }
            response = requests.post(self.api_url, headers=self.headers, json=data)
            self.redis_util.set_json(f'starbot:friend_or_group_info:{account.get("instanceId")}', response.json().get('data'))
        return response.json()
