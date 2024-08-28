from flask import current_app as app, copy_current_request_context
from flask import render_template, request, jsonify, Response, session
import json
import time
from . import article_bp
from services.article_service import comment, hook,simulate_human

@article_bp.route('/rewrite', methods=['GET'])
def rewrite():
    return render_template('rewrite.html')

@article_bp.route('/do_rewrite', methods=['POST'])
def do_rewrite():
    data = request.get_json()
    uuid = data.get('uuid', '')
    session[uuid] = data
    # content = data.get('content', '')
    # translate = data.get('translate', False)
    
    # print(f"接收到的内容: {content}")
    # print(f"是否需要翻译: {translate}")
    
    # 这里可以添加处理逻辑，例如保存到数据库或开始后台任务
    
    return jsonify({"success": True, "message": "开始处理"})

@article_bp.route('/do_rewrite_stream')
def do_rewrite_stream():
    uuid = request.args.get('uuid')
    data = session.get(uuid)
    content = data.get('content', '')
    translate = data.get('translate', False)
    
    ctx = app.app_context()
    @copy_current_request_context
    def generate():
        yield "data: " + json.dumps({"step": "show_toast", "content": "正在生成锐评"}) + "\n\n"
        with ctx:
            # 步骤1：点评
            comment_content = comment(content)
            # comment_content = simulate_human(comment_content)
        yield "data: " + json.dumps({"step": "comment", "content": comment_content}) + "\n\n"
        yield "data: " + json.dumps({"step": "show_toast", "content": "正在生成钩子"}) + "\n\n"
        time.sleep(1)  # 模拟处理时间
        with ctx:
            # 步骤2：钩子
            hook_content = "" #hook(content)
            yield "data: " + json.dumps({"step": "hook", "content": hook_content}) + "\n\n"
        # 步骤2：写文章因子
        yield "data: " + json.dumps({"step": "factors", "content": "文章因子..."}) + "\n\n"
        time.sleep(1)  # 模拟处理时间

        # 步骤3：总结点评
        yield "data: " + json.dumps({"step": "summary", "content": "总结点评..."}) + "\n\n"
        time.sleep(1)  # 模拟处理时间

        # 结束
        yield "data: " + json.dumps({"step": "complete", "content": "洗稿完成"}) + "\n\n"

    # 删除这个uuid的session
    del session[uuid]
    return Response(generate(), content_type='text/event-stream')