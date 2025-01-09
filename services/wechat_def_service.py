from lib import itchat
import json
from utils.mem0ai_util import add as mem0ai_add
from services.wechat_service import simple_reply
from utils.redis_util import RedisUtil
from models.wechat_user import WechatUser


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
    friends_cache = itchat.get_friends(update=False)
    RedisUtil().set_value('friends_cache', json.dumps(friends_cache, ensure_ascii=False, indent=2))
    print("Friends cache updated:")
    print(json.dumps(friends_cache, ensure_ascii=False, indent=2))

def update_groups_cache():
    groups_cache = itchat.get_chatrooms(update=False)
    RedisUtil().set_value('groups_cache', json.dumps(groups_cache, ensure_ascii=False, indent=2))
    print("Groups cache updated:")
    print(json.dumps(groups_cache, ensure_ascii=False, indent=2))


def get_friend_by_nickname(name):
    friends_cache = RedisUtil().get_value('friends_cache')
    if friends_cache is None:
        update_friends_cache()
    # 将取回的值转换为 JSON 对象
    friends_cache = json.loads(friends_cache)
    return next((friend for friend in friends_cache if 
                 friend['UserName'] == name or 
                 friend['NickName'] == name or 
                 friend['RemarkName'] == name), None)

def get_group_by_name(name):
    groups_cache = RedisUtil().get_value('groups_cache')
    if groups_cache is None:
        update_groups_cache()
    # 将取回的值转换为 JSON 对象
    groups_cache = json.loads(groups_cache)
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
    
    # 获取用户信息
    user = msg['User']
    sender_nickname = user['NickName']
    sender_sex = '男' if user['Sex'] == 1 else '女' if user['Sex'] == 2 else '未知'
    sender_signature = user['Signature']
    sender_address = user['Province'] + user['City']
    WechatUser.create_user(nickname=sender_nickname,base_info=f'姓名:{sender_nickname},性别:{sender_sex},地址:{sender_address},个性签名:{sender_signature}。')
    # mem0_msg = [
    #     {
    #         'role':'user',
    #         'content':f'我叫{sender_nickname},性别{sender_sex},地址{sender_address},个性签名{sender_signature}'
    #     },
    #     {
    #         'role':'assistant',
    #         'content':"好的，我记住了"
    #     }
    # ]
    # mem0ai_add(mem0_msg,sender_nickname)
    # 获取消息内容
    content = msg['Text']

    # 调用simple_reply获取AI反馈
    ai_response = simple_reply('single_user',sender_nickname,sender_nickname,content)

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
    # 检查消息是否以 "@杨九月儿" 或 "九月" 开头
    if not (content.startswith("@mark") or content.startswith("mark")):
        return  # 如果不是，直接返回，不做任何处理
    # 去掉开头的@杨九月儿或者九月
    content = content.lstrip("@mark").lstrip("mark").strip()
    # 群名
    chatroom_nikename = msg['User']['NickName']
    # 获取群聊的用户名
    group_id = msg['FromUserName']
    # 获取发送消息的群成员的用户名
    sender = msg['ActualNickName']
    # 从群成员列表中找到对应的成员，并获取其NickName
    # 从群成员列表中找到对应的成员，并获取其NickName和UserName
    sender_info = next(({"NickName": member['NickName'], "UserName": member['UserName']} 
                        for member in msg['User']['MemberList'] 
                        if member['DisplayName'] == sender), 
                       {"NickName": "未知用户", "UserName": ""})

    sender_nickname = sender_info["NickName"] if sender_info["NickName"] != "未知用户" else sender
    # sender_username = sender_info["UserName"]
    
    # 调用simple_reply获取AI反馈
    ai_response = simple_reply('chat_room',chatroom_nikename,sender_nickname,content)
    


    # 构造回复消息，包含发送者的昵称
    reply = f"@{sender}\n{ai_response}"

    # 发送AI反馈给群聊
    itchat.send(reply, toUserName=group_id)