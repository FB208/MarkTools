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
    itchat.run()
    return jsonify({"status": "success"})
    

@wechat_bp.route('/tempfiles/<path:filename>')
def serve_qr(filename):
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
        friend = wechat_def_service.get_friend_by_nickname(target)
        if friend:
            wechat_def_service.send_message_to_friend(friend['UserName'], message)
            return jsonify({"status": "success", "message": "消息已发送给好友"})
        else:
            return jsonify({"status": "error", "message": "未找到指定好友"})
    elif message_type == 'group':
        group = wechat_def_service.get_group_by_name(target)
        if group:
            wechat_def_service.send_message_to_group(group['UserName'], message)
            return jsonify({"status": "success", "message": "消息已发送到群聊"})
        else:
            return jsonify({"status": "error", "message": "未找到指定群聊"})
    else:
        return jsonify({"status": "error", "message": "不支持的消息类型"})