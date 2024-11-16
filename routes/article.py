from flask import current_app as app, copy_current_request_context, stream_with_context
from flask import render_template, request, jsonify, Response, session
import json
import time
from . import article_bp
from services.article_service import comment, hook,simulate_human,rewrite_body,title,rewrite_body_master
from services.translate_service import expert_translate
from utils.md_util import remove_markdown_links
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
    simple_translate = data.get('simple_translate', False)
    translate = data.get('translate', False)
    master = data.get('master', False)
    '''
    {
        "advanced setting": {
            "commentBias": "锐评偏向性"
        }
    }
    '''
    advanced_settings = data.get('advanced_settings', {})

    
    ctx = app.app_context()
    @copy_current_request_context
    def generate():
        if simple_translate:
            yield "data: " + json.dumps({"step": "show_toast", "content": "正在翻译"}) + "\n\n"
            with ctx:
                translate_content = simulate_human(content)
                yield "data: " + json.dumps({"step": "translate", "content": translate_content}) + "\n\n" 
                time.sleep(3)
                yield "data: " + json.dumps({"step": "complete", "content": "洗完洗完"}) + "\n\n"
        else:
            # 处理markdown链接
            clear_content = remove_markdown_links(content)
            # 步骤1：锐评
            yield "data: " + json.dumps({"step": "show_toast", "content": "正在生成锐评"}) + "\n\n"
            with ctx:
                comment_content = comment(clear_content,advanced_settings.get('commentBias',''))
                # comment_content = simulate_human(comment_content)
            yield "data: " + json.dumps({"step": "comment", "content": comment_content}) + "\n\n"
            
            
            # 步骤2：钩子
            hook_content=""
            yield "data: " + json.dumps({"step": "show_toast", "content": "正在生成钩子"}) + "\n\n"
            with ctx:
                hook_content = hook(clear_content)
                yield "data: " + json.dumps({"step": "hook", "content": hook_content}) + "\n\n"
            
            
            # 步骤3：翻译
            translate_content = clear_content
            if translate:
                yield "data: " + json.dumps({"step": "show_toast", "content": "正在翻译，专家翻译超慢哦~"}) + "\n\n"
                with ctx:
                    translate_content = expert_translate(clear_content)
                    yield "data: " + json.dumps({"step": "translate", "content": translate_content}) + "\n\n"


            # 步骤4：洗稿
            rewrite_content = ""
            yield "data: " + json.dumps({"step": "show_toast", "content": "正在优化文案"}) + "\n\n"
            with ctx:
                if master:
                    rewrite_content = rewrite_body_master(translate_content)
                else:
                    rewrite_content = rewrite_body(translate_content)
            yield "data: " + json.dumps({"step": "body", "content": rewrite_content}) + "\n\n"


            # 步骤5：优选标题
            title_temp_content = rewrite_content+"\\n"+hook_content
            title_content=""
            yield "data: " + json.dumps({"step": "show_toast", "content": "正在优选标题"}) + "\n\n"
            with ctx:
                title_content = title(title_temp_content)
            yield "data: " + json.dumps({"step": "title", "content": title_content}) + "\n\n"
            
            # 结束
            yield "data: " + json.dumps({"step": "complete", "content": "洗完洗完"}) + "\n\n"

    # 删除这个uuid的session
    del session[uuid]
    return Response(generate(), content_type='text/event-stream')

# 文稿校验
@article_bp.route('/verify', methods=['GET'])
def verify():
    return render_template('verify.html')


@article_bp.route('/do_verify_stream')
def do_verify_stream():
    content = request.args.get('content')
    if not content:
        return jsonify({'error': '内容不能为空'}), 400
    
    @stream_with_context
    def generate():
        yield "data: " + json.dumps({"step": "show_toast", "content": "开始校验文稿"}) + "\n\n"
        
        # 这里是校验逻辑,您可以根据需要自行实现
        # verify_result = your_verify_function(content)
        verify_result = "这里是校验结果"  # 临时占位
        
        yield "data: " + json.dumps({"step": "verify_result", "content": verify_result}) + "\n\n"
        
        yield "data: " + json.dumps({"step": "complete", "content": "校验完成"}) + "\n\n"

    return Response(generate(), mimetype='text/event-stream')

@article_bp.route('/workreport', methods=['GET'])
def workreport():
    return render_template('workreport.html')

@article_bp.route('/do_workreport_stream')
def do_workreport_stream():
    content = request.args.get('content')
    if not content:
        return jsonify({'error': '内容不能为空'}), 400
    
    @stream_with_context
    def generate():
        yield "data: " + json.dumps({"step": "show_toast", "content": "开始生成怼咕报告"}) + "\n\n"
        
        # 这里是生成怼咕报告的逻辑
        report_result = "这里是怼咕报告内容"  # 临时占位
        
        yield "data: " + json.dumps({"step": "report_result", "content": report_result}) + "\n\n"
        
        yield "data: " + json.dumps({"step": "complete", "content": "生成完成"}) + "\n\n"

    return Response(generate(), mimetype='text/event-stream')
