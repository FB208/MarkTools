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
        data = {
            "type": "getAccountListRequest",
            "params": {
                "status": 1
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=data)
        
        self.redis_util.array_add_or_replace('starbot:account_list', response.json().get('data'))
        return response.json()

    def get_group_list(self):
        account_list = self.redis_util.array_get_all('starbot:account_list')
        for account in account_list:
            data = {
                "type": "getGroupList",
                "params": {
                    "instanceId": account.get('instanceId'),
                    "cache": 0
                }
            }
            response = requests.post(self.api_url, headers=self.headers, json=data)
            self.redis_util.array_add_or_replace(f'starbot:group_list:{account.get("instanceId")}', response.json().get('data'))
        return response.json()

    def get_friend_list(self):
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
            self.redis_util.array_add_or_replace(f'starbot:friend_list:{account.get("instanceId")}', response.json().get('data'))
        return response.json()
