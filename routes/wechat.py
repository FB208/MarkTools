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
from services.wechat_service import simple_reply
import json
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
            tempfiles_dir = os.path.join('tempfiles')
            os.makedirs(tempfiles_dir, exist_ok=True)

            # 保存二维码图片，使用时间戳作为文件名的一部分
            qr_filename = f'qr_{timestamp}.png'
            qr_path = os.path.join(tempfiles_dir, qr_filename)
            img.save(qr_path)
            
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
    

@itchat.msg_register('Text')
def text_reply(msg):
    print("收到的消息:")
    # print(json.dumps(msg, ensure_ascii=False, indent=2))
    '''
{
  "MsgId": "677103519078355447",
  "FromUserName": "@0f15abd887c5669cc9455cbaf039157bb6d39c5300d8626527bbda5692d027db",
  "ToUserName": "@48526c320137f4d97226fbd4e8e62c4f1b55967b5851468d8157e939e8ebf85f",
  "MsgType": 1,
  "Content": "你好",
  "Status": 3,
  "ImgStatus": 1,
  "CreateTime": 1726724473,
  "VoiceLength": 0,
  "PlayLength": 0,
  "FileName": "",
  "FileSize": "",
  "MediaId": "",
  "Url": "",
  "AppMsgType": 0,
  "StatusNotifyCode": 0,
  "StatusNotifyUserName": "",
  "RecommendInfo": {
    "UserName": "",
    "NickName": "",
    "QQNum": 0,
    "Province": "",
    "City": "",
    "Content": "",
    "Signature": "",
    "Alias": "",
    "Scene": 0,
    "VerifyFlag": 0,
    "AttrStatus": 0,
    "Sex": 0,
    "Ticket": "",
    "OpCode": 0
  },
  "ForwardFlag": 0,
  "AppInfo": {
    "AppID": "",
    "Type": 0
  },
  "HasProductId": 0,
  "Ticket": "",
  "ImgHeight": 0,
  "ImgWidth": 0,
  "SubMsgType": 0,
  "NewMsgId": 677103519078355447,
  "OriContent": "",
  "EncryFileName": "",
  "User": {
    "MemberList": [],
    "Uin": 0,
    "UserName": "@0f15abd887c5669cc9455cbaf039157bb6d39c5300d8626527bbda5692d027db",
    "NickName": "杨惠超",
    "HeadImgUrl": "/cgi-bin/mmwebwx-bin/webwxgeticon?seq=738861747&username=@0f15abd887c5669cc9455cbaf039157bb6d39c5300d8626527bbda5692d027db&skey=@crypt_1d0296d7_b11077f7306b44aa6cbf43974d926341",
    "ContactFlag": 3,
    "MemberCount": 0,
    "RemarkName": "",
    "HideInputBarFlag": 0,
    "Sex": 1,
    "Signature": "知而不行，只是未知",
    "VerifyFlag": 0,
    "OwnerUin": 0,
    "PYInitial": "YHC",
    "PYQuanPin": "yanghuichao",
    "RemarkPYInitial": "",
    "RemarkPYQuanPin": "",
    "StarFriend": 0,
    "AppAccountFlag": 0,
    "Statues": 0,
    "AttrStatus": 33660967,
    "Province": "天津",
    "City": "河东",
    "Alias": "",
    "SnsFlag": 305,
    "UniFriend": 0,
    "DisplayName": "",
    "ChatRoomId": 0,
    "KeyWord": "yan",
    "EncryChatRoomId": "",
    "IsOwner": 0
  },
  "Type": "Text",
  "Text": "你好"
}
    '''
    # 获取发送者的用户名
    from_user = msg['FromUserName']
    # 获取消息内容
    content = msg['Text']

    # 调用simple_reply获取AI反馈
    ai_response = simple_reply(content)

    # 发送AI反馈给用户
    itchat.send(ai_response, toUserName=from_user)

def exitCallback():
    print("Exit success")

def loginCallback():
    print("Login success")
    


@wechat_bp.route('/tempfiles/<path:filename>')
def serve_qr(filename):
    return send_from_directory('tempfiles', filename)