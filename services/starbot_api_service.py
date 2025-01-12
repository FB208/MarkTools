from flask import current_app as app
import requests
from utils.redis_util import RedisUtil
from models.starbot_friend import StarbotFriend

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
            robot_info = self.redis_util.get_json(f'starbot:robot_info:{account.get("instanceId")}')
            response = requests.post(self.api_url, headers=self.headers, json=data)
            self.redis_util.array_add_or_replace(f'starbot:friend_list:robotId_{robot_info.get("robotId")}', response.json().get('data'))
            # 微信好友信息入库
            for friend in response.json().get('data'):
                wx_id = friend.get('wxId')
                db_friend = StarbotFriend.get_by_wx_id(wx_id)
                if db_friend:
                    continue
                else:
                    base_info =     {
                        '姓名': friend.get('nickname'), 
                        '性别': {0: '未知', 1: '男', 2: '女'}.get(friend.get('Gender'), '未知'), 
                        '祖籍':'',
                        '现住址': '',
                        '生日': '',
                        '职业': '',
                        '兴趣爱好': '',
                        '简介': ''
                    }
                    StarbotFriend.create_friend(wx_id=wx_id, base_info=base_info, personality_summary='')
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

    def send_text_message(self, robotId, toWxId, message):
        '''
        发送文本消息
        robotId: 机器人ID(发送方)
        toWxId: 接收方微信ID,群聊时为groupId
        message: 发送的消息；
                 群聊使用如下格式：[@,wxid=\"接收方微信ID\",nick=,isAuto=true] 这是要发送的消息
        '''
        data = {
            "type": "sendTextMessage",
            "params": {
                "robotId": robotId,
                "wxId": toWxId,
                "message": message
                }
            }   
        response = requests.post(self.api_url, headers=self.headers, json=data)
        print(response.json())
        return response.json()
