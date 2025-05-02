from flask import current_app as app
from flask import render_template, request, jsonify
from . import wechat_sub_account_bp
from services.wechat_sub_account_service import process_text_content
import xml.etree.ElementTree as ET
from models.wechat_user import WechatUser
import time
import logging
import threading
import hashlib

# 设置与微信公众平台配置一致的Token
TOKEN = "你设置的token"  # 替换为你在微信公众平台设置的Token

@wechat_sub_account_bp.route('/wsa/msg', methods=['GET', 'POST'])
def msg():
    if request.method == 'GET':
        # 处理微信服务器的验证请求
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        # 按照微信的验证规则进行验证
        temp_list = [TOKEN, timestamp, nonce]
        temp_list.sort()
        temp_str = ''.join(temp_list)
        hash_obj = hashlib.sha1()
        hash_obj.update(temp_str.encode('utf-8'))
        hashcode = hash_obj.hexdigest()
        
        # 验证签名
        if hashcode == signature:
            return echostr
        else:
            return "验证失败"
    
    elif request.method == 'POST':
        try:
            # 获取XML消息数据
            xml_data = request.data
            # 打印接收到的原始XML数据到控制台
            print("接收到微信订阅号消息:")
            print(xml_data.decode('utf-8'))
            
            # 解析XML数据
            root = ET.fromstring(xml_data)
            msg_type = root.find('MsgType').text
            from_user = root.find('FromUserName').text
            to_user = root.find('ToUserName').text
            create_time = root.find('CreateTime').text
            return_content = ""
            
            # 根据消息类型打印不同的信息
            if msg_type == 'text':
                content = root.find('Content').text
                response = process_text_content(from_user,content)
                print(f"用户 {from_user} 发送文本消息: {content}")
                return_content= response
            elif msg_type == 'image':
                pic_url = root.find('PicUrl').text
                media_id = root.find('MediaId').text
                print(f"用户 {from_user} 发送图片消息: {pic_url}")
                return_content = "暂不支持图片消息"
            elif msg_type == 'voice':
                media_id = root.find('MediaId').text
                format = root.find('Format').text
                print(f"用户 {from_user} 发送语音消息，格式: {format}")
                return_content = "暂不支持语音消息"
            elif msg_type == 'event':
                event = root.find('Event').text
                print(f"用户 {from_user} 触发事件: {event}")
                if event == "subscribe":
                    threading.Thread(
                        target=lambda: WechatUser.create_user(open_id=from_user, subscribe=1),
                        daemon=True
                    ).start()
                    return_content = """感谢关注生产力Mark~
1. AI前沿资讯
2. 各种绿色版软件，有额外需求可以私信，我会为你单独做一期
3. 私信除了能找资源外，还是个非常好用的对话式AI（基于GLM-4调优）
4. 限时免费：https://tools.agnet.top"""
                elif event == "unsubscribe":
                    def delete_user_thread():
                        unsub_user = WechatUser.get_by_open_id(from_user)
                        unsub_user.update_info(subscribe=0)
                    threading.Thread(
                        target=lambda: delete_user_thread,
                        daemon=True
                    ).start()
                    return_content = "取关后不支持重新关注，你再也找不到回复几个数字就能免费获取资源的方法了，江湖再见，后会无期~"
                    
            # 返回空字符串或简单的回复消息
            reply = f"""
            <xml>
                <ToUserName><![CDATA[{from_user}]]></ToUserName>
                <FromUserName><![CDATA[{to_user}]]></FromUserName>
                <CreateTime>{int(time.time())}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{return_content}]]></Content>
            </xml>
            """
            return reply
            
        except Exception as e:
            print(f"处理微信消息时出错: {str(e)}")
            logging.error(f"处理微信消息时出错: {str(e)}")
            return "success"

