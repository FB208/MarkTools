from flask import current_app as app, send_file
from flask import render_template, request, jsonify
from . import wechat_bp
from concurrent.futures import ThreadPoolExecutor
import os
import time
from lib import itchat
import base64
import threading
import io
from flask import send_from_directory
import json
import services.wechat_def_service as wechat_def_service
from utils.redis_util import RedisUtil

@wechat_bp.route('/wechat/login')
def wechat_login():
    return render_template('wechat.html')
@wechat_bp.route('/wechat/login_post', methods=['GET'])
def wechat_login_post():
    timestamp = request.args.get('timestamp')
    def qrCallback(uuid, status, qrcode):
    # logger.debug("qrCallback: {} {}".format(uuid,status))
        if status == "0":
            try:
                from PIL import Image

                img = Image.open(io.BytesIO(qrcode))
                _thread = threading.Thread(target=img.show, args=("QRCode",))
                _thread.setDaemon(True)
                _thread.start()
            except Exception as e:
                pass

            import qrcode

            url = f"https://login.weixin.qq.com/l/{uuid}"

            qr_api1 = "https://api.isoyu.com/qr/?m=1&e=L&p=20&url={}".format(url)
            qr_api2 = "https://api.qrserver.com/v1/create-qr-code/?size=400×400&data={}".format(url)
            qr_api3 = "https://api.pwmqr.com/qrcode/create/?url={}".format(url)
            qr_api4 = "https://my.tv.sohu.com/user/a/wvideo/getQRCode.do?text={}".format(url)
            print("You can also scan QRCode in any website below:")
            print(qr_api3)
            print(qr_api4)
            print(qr_api2)
            print(qr_api1)
            # _send_qr_code([qr_api3, qr_api4, qr_api2, qr_api1])
            qr = qrcode.QRCode(border=1)
            qr.add_data(url)
            qr.make(fit=True)
            # qr.print_ascii(invert=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            # 确保tempfiles文件夹存在
            tempfiles_dir = os.path.join(app.config['BASE_PATH'], 'tempfiles')
            os.makedirs(tempfiles_dir, exist_ok=True)

            # 保存二维码图片，使用时间戳作为文件名的一部分
            qr_filename = f'qr_{timestamp}.png'
            qr_path = os.path.join(tempfiles_dir, qr_filename)
            img.save(qr_path)
    
    def exitCallback():
        print("Exit success")

    def loginCallback():
        wechat_def_service.refresh_caches()
        print("Login success")
    # 登录微信
    itchat.auto_login(
        enableCmdQR=2,
        hotReload=False,
        qrCallback=qrCallback,
        exitCallback=exitCallback,
        loginCallback=loginCallback
    )
    
    # 发送测试消息给文件传输助手
    # itchat.send('这是一条测试消息', toUserName='filehelper')
    # 在auto_login之后添加
    
    
    def handle_message(data):
        '''
        {
            "nickname": "nickname",
            "msg": "msg",
            "type": "friend"/group
        }
        '''
        try:
            data = json.loads(data)
            nickname = data.get('nickname')
            msg = data.get('msg')
            msg_type = data.get('type')
            if msg_type == "friend":
                friend = wechat_def_service.get_friend_by_nickname(nickname)
                if friend:
                    wechat_def_service.send_message_to_friend(friend['UserName'], msg)
            elif msg_type == "group":
                group = wechat_def_service.get_group_by_name(nickname)
                if group:
                    wechat_def_service.send_message_to_group(group['UserName'], msg)
        except json.JSONDecodeError as e:
            print(f"Error decoding message: {e}")
        except Exception as e:
            print(f"Error sending message: {e}")

    redis_util = RedisUtil()
    threading.Thread(target=redis_util.listen, args=('wechat_cmd', handle_message), daemon=True).start()
    itchat.run()
    # threading.Thread(target=itchat.run, daemon=True).start()
    return jsonify({"status": "success"})
    

@wechat_bp.route('/tempfiles/<path:filename>')
def serve_qr(filename):
    print(os.path.join(app.config['BASE_PATH'], 'tempfiles'), filename)
    return send_from_directory(os.path.join(app.config['BASE_PATH'], 'tempfiles'), filename)

@wechat_bp.route('/wechat/refresh_cache', methods=['GET'])
def refresh_cache():
    wechat_def_service.refresh_caches()
    return jsonify({"status": "success", "message": "缓存已刷新"})

# 发送消息
@wechat_bp.route('/wechat/send_message', methods=['GET'])
def send_message():
    return render_template('wechat_send_message.html')

@wechat_bp.route('/wechat/send_message', methods=['POST'])
def send_message_post():
    data = request.json
    message_type = data.get('type')
    target = data.get('target')
    message = data.get('message')

    if message_type == 'friend':
        try:
            # friend = wechat_def_service.get_friend_by_nickname(target)
            friends = itchat.search_friends(name=target)
            friend=friends[0]['UserName']
            wechat_def_service.send_message_to_friend(friend, message)
            # RedisUtil().publish_message('wechat_cmd', json.dumps({"nickname": target, "msg": message, "type": "friend"}))
            return jsonify({"status": "success", "message": "消息已发送给好友"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    elif message_type == 'group':
        try:
            # group = wechat_def_service.get_group_by_name(target)
            groups = itchat.search_chatrooms(name=target)
            group=groups[0]['UserName']
            wechat_def_service.send_message_to_group(group, message)
            # RedisUtil().publish_message('wechat_cmd', json.dumps({"nickname": target, "msg": message, "type": "group"}))
            return jsonify({"status": "success", "message": "消息已发送到群聊"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": "不支持的消息类型"})
