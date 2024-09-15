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

@wechat_bp.route('/wechat/login')
def wechat_login():
    return render_template('wechat.html')
@wechat_bp.route('/wechat/login_post', methods=['GET'])
def wechat_login_post():
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
    
    
    return jsonify({"status": "success"})
    
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
        qr.print_ascii(invert=True)
        
def exitCallback():
    print("Exit success")

def loginCallback():
    print("Login success")