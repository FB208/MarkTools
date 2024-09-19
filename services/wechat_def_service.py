from lib import itchat
import json
from utils.mem0ai_util import add_message
from services.wechat_service import simple_reply



# 全局变量用于缓存
friends_cache = None
groups_cache = None

def send_message_to_friend(friend_username, message):
    """
    向指定好友发送消息
    """
    itchat.send(message, toUserName=friend_username)

def send_message_to_group(group_username, message):
    """
    向指定群聊发送消息
    """
    itchat.send(message, toUserName=group_username)

def send_message_to_file_helper(message):
    """
    向文件传输助手发送消息
    """
    itchat.send(message, toUserName='filehelper')
def update_friends_cache():
    global friends_cache
    friends_cache = itchat.get_friends(update=True)
    print("Friends cache updated:")
    print(json.dumps(friends_cache, ensure_ascii=False, indent=2))

def update_groups_cache():
    global groups_cache
    groups_cache = itchat.get_chatrooms(update=True)
    print("Groups cache updated:")
    print(json.dumps(groups_cache, ensure_ascii=False, indent=2))


def get_friend_by_nickname(name):
    global friends_cache
    if friends_cache is None:
        update_friends_cache()
    return next((friend for friend in friends_cache if 
                 friend['UserName'] == name or 
                 friend['NickName'] == name or 
                 friend['RemarkName'] == name), None)

def get_group_by_name(name):
    global groups_cache
    if groups_cache is None:
        update_groups_cache()
    return next((group for group in groups_cache if 
                 group['UserName'] == name or 
                 group['NickName'] == name or 
                 group['RemarkName'] == name), None)

def refresh_caches():
    update_friends_cache()
    update_groups_cache()
# 接收用户消息
@itchat.msg_register('Text')
def text_reply(msg):
    # print("收到的消息:")
    # 完整消息在这 https://mark-up.notion.site/itchat-106a2321d4fb802c81bfd9a2f2234d00?pvs=4
    # print(json.dumps(msg, ensure_ascii=False, indent=2))
    # 获取发送者的用户名
    from_user = msg['FromUserName']
    # 获取消息内容
    content = msg['Text']

    # 调用simple_reply获取AI反馈
    ai_response = simple_reply(content)

    # 发送AI反馈给用户
    itchat.send(ai_response, toUserName=from_user)
    
# 接收群消息
@itchat.msg_register('Text', isGroupChat=True)
def group_text_reply(msg):
    print("收到群消息:")
    # print(json.dumps(msg, ensure_ascii=False, indent=2))
    # 完整消息在这 https://mark-up.notion.site/itchat-106a2321d4fb80208a1dead0d2cd8e4d?pvs=4
    # 获取消息内容
    content = msg['Content']
    
    # 获取群聊的用户名
    group_id = msg['FromUserName']
    # 获取发送消息的群成员的用户名
    sender = msg['ActualNickName']

    # 调用simple_reply获取AI反馈
    ai_response = simple_reply(content)

    # 构造回复消息，包含发送者的昵称
    reply = f"@{sender}\n{ai_response}"

    # 发送AI反馈给群聊
    itchat.send(reply, toUserName=group_id)