from flask import render_template, request, jsonify, current_app,stream_with_context as app
from flask import render_template, request, jsonify, Response, session
from . import html2pic_bp
import queue
import json
from llm.llm_factory import LLMFactory
from prompts import html2pic_prompt

@html2pic_bp.route('/', methods=['GET'])
def index():
    """
    HTML转图片功能首页
    """
    return render_template('html2pic/index.html')

@html2pic_bp.route('/generate_redbook', methods=['POST'])
def generate_redbook():
    data = request.get_json()
    text_content = data.get('text_content', '')
    
    def get_wen_an(origin_content):
        messages = [
            {"role": "system", "content": html2pic_prompt.wenan_system_prompt()},
            {"role": "user", "content": origin_content}
        ]
        llm_service = LLMFactory.get_llm_service("longcat")
        completion = llm_service.get_chat_completion(messages=messages)
        wenan = llm_service.get_messages(completion)
        return wenan
    
    result_queue = queue.Queue()
    @copy_current_request_context
    def generate_kapian_async(index,chaifen_content,chat_history,result_queue):
        with app.app_context():
            messages = [
                {"role": "system", "content": lighthouse_redbook_prompt.kapian_system_prompt(index)},
                {"role": "user", "content": convert_to_string(chaifen_content)}
            ]
            llm_service = LLMFactory.get_llm_service(kapian_platform)
            completion = llm_service.get_chat_completion(model=kapian_model, messages=messages)
            kapian = llm_service.clear_thinking_msg(completion)
            kapian_html = kapian.replace('```html', '').replace('```', '').strip()
            kapian_html = convert_to_string(kapian_html)
            log.info(f"生成卡片: {kapian_html}")
            result_queue.put(kapian_html)
            
    def generate():
        # 立即发送一个心跳数据,保持连接活跃
        yield f"data: {json.dumps({'type': 'heartbeat', 'status': 'success', 'content': '连接已建立'})}\n\n"
        

        wenan = get_wen_an(text_content)
        yield f"data: {json.dumps({'type': 'text', 'status': 'success', 'content': wenan})}\n\n"
        chaifen = chaifen_wenan(wenan)
        

        for index,chaifen_content in enumerate(chaifen):
            kapian_html = generate_kapian(index,chaifen_content,wenan)
            yield f"data: {json.dumps({'type': f'pic', 'status': 'success', 'content': kapian_html})}\n\n"
        '''
        # 创建线程列表
        threads = []
        for index,chaifen_content in enumerate(chaifen):
            thread_kapian = threading.Thread(
                target=generate_kapian_async,
                args=(index, chaifen_content,chat_history,result_queue),
                daemon=True
            )
            threads.append(thread_kapian)
            
        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待并返回所有卡片结果
        received = 0
        while received < len(chaifen):
            try:
                result = result_queue.get(timeout=1)  # 设置超时防止无限等待
                log.info(f"生成卡片结果: {result}")
                # return_content = result.get("content")
                yield f"data: {json.dumps({'type': f'pic', 'status': 'success', 'content': result})}\n\n"
                received += 1
            except queue.Empty:
                continue
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        '''
        yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '生成完成'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')