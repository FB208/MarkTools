from flask import render_template, request, jsonify, current_app as app
from flask import render_template, request, jsonify, Response, session,stream_with_context
from flask import send_file
from . import html2pic_bp
import queue
import threading
import json
from llm.llm_factory import LLMFactory
from prompts import html2pic_prompt
from utils.json_util import check_json, robust_parse_json_like
from utils.text_util import convert_to_string
import io
import zipfile
import base64
import time
import requests

@html2pic_bp.route('/html2pic', methods=['GET'])
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
        llm_service = LLMFactory.get_llm_service("or")
        completion = llm_service.get_chat_completion(model="x-ai/grok-4-fast:free",messages=messages)
        wenan = llm_service.get_messages(completion)
        return wenan
    
    
    def chaifen_wenan(wenan):
        json_schema = {
            "data":[]
        }
        messages = [
            {"role": "system", "content": html2pic_prompt.chaifen_system_prompt()},
            {"role": "user", "content": wenan}
        ]
        llm_service = LLMFactory.get_llm_service("or")
        completion = llm_service.get_json_completion(model="x-ai/grok-4-fast:free",messages=messages)
        chaifen = llm_service.get_messages(completion)

        obj = robust_parse_json_like(chaifen, max_unwrap=2)
        chaifen_data = obj.get('data', []) if isinstance(obj, dict) else []
        return chaifen_data
        # max_retries = 3
        # retry_count = 0
        # while retry_count <= max_retries:
        #     llm_service = LLMFactory.get_llm_service("longcat")
        #     completion = llm_service.get_json_completion(messages=messages)
        #     chaifen = llm_service.get_messages(completion)
        #     is_valid, error = check_json(chaifen, json_schema)
        #     if is_valid:
        #         return json.loads(chaifen)['data']
        #     retry_count += 1
            
            
    def generate():
        # 立即发送一个心跳数据,保持连接活跃
        yield f"data: {json.dumps({'type': 'heartbeat', 'status': 'success', 'content': '连接已建立'})}\n\n"
        

        wenan = get_wen_an(text_content)
        yield f"data: {json.dumps({'type': 'text', 'status': 'success', 'content': wenan})}\n\n"
        chaifen = chaifen_wenan(wenan)
        

        # for index,chaifen_content in enumerate(chaifen):
        #     kapian_html = generate_kapian(index,chaifen_content,wenan)
        #     yield f"data: {json.dumps({'type': f'pic', 'status': 'success', 'content': kapian_html})}\n\n"

        # 使用字典存储结果，支持实时返回和顺序保证
        results = {}
        results_lock = threading.Lock()
        next_index_to_yield = 0
        
        def generate_kapian_async(index, chaifen_content, results_dict, lock, flask_app):
            with flask_app.app_context():
                messages = [
                    {"role": "system", "content": html2pic_prompt.kapian_system_prompt(index)},
                    {"role": "user", "content": convert_to_string(chaifen_content)}
                ]
                llm_service = LLMFactory.get_llm_service("gb")
                completion = llm_service.get_chat_completion(model="gemini-2.5-pro",messages=messages)
                kapian = llm_service.get_messages(completion)
                kapian_html = kapian.replace('```html', '').replace('```', '').strip()
                kapian_html = convert_to_string(kapian_html)
                
                # 线程安全地存储结果
                with lock:
                    results_dict[index] = kapian_html

        # 创建线程列表
        threads = []
        flask_app = app._get_current_object()
        for index,chaifen_content in enumerate(chaifen):
            thread_kapian = threading.Thread(
                target=generate_kapian_async,
                args=(index, chaifen_content, results, results_lock, flask_app),
                daemon=True
            )
            threads.append(thread_kapian)
            
        # 启动所有线程
        for thread in threads:
            thread.start()

        # 按顺序返回结果，即使某些结果还未完成也要等待
        for i in range(len(chaifen)):
            # 等待第i个结果完成
            while i not in results:
                # 检查是否所有线程都已结束（避免死锁）
                if all(not thread.is_alive() for thread in threads):
                    break
                # 短暂等待
                threading.Event().wait(0.1)
            
            if i in results:
                yield f"data: {json.dumps({'type': f'pic', 'status': 'success', 'content': results[i]})}\n\n"
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()

        yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '生成完成'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        }
    )


@html2pic_bp.route('/download_images', methods=['POST'])
def download_images():
    """
    接收前端传来的图片HTML数组，调用外部服务渲染为PNG图片，并打包为ZIP返回下载。
    请求JSON参数：
    {
      "html_list": ["<div>...</div>", ...],
      "width": 600,
      "height": 800,
      "watermark_text": "",
      "watermark_image_url": ""
    }
    """
    data = request.get_json(silent=True) or {}
    html_list = data.get('html_list', [])
    width = int(data.get('width', 600) or 600)
    height = int(data.get('height', 800) or 800)
    watermark_text = data.get('watermark_text', '') or ''
    watermark_image_url = data.get('watermark_image_url', '') or ''

    if not isinstance(html_list, list) or len(html_list) == 0:
        return jsonify({
            'status': 'error',
            'message': 'html_list 不能为空且必须为数组'
        }), 400

    service_url = 'https://mt.agnet.top/image/url2png'

    def render_html_to_png_bytes(html_string: str) -> bytes:
        html_b64 = base64.b64encode(html_string.encode('utf-8')).decode('utf-8')
        payload = {
            'html_base64': html_b64,
            'width': width,
            'height': height,
            'watermark_text': watermark_text,
            'watermark_image_url': watermark_image_url,
            'response_type': 'base64'
        }
        resp = requests.post(service_url, json=payload, timeout=60)
        resp.raise_for_status()

        # 外部服务返回结构固定：
        # {
        #   "success": true,
        #   "data": { "image_base64": "" },
        #   "message": "ok",
        #   "status": 200
        # }
        obj = resp.json()
        if not isinstance(obj, dict):
            raise RuntimeError('外部服务返回非JSON对象')
        if not obj.get('success'):
            raise RuntimeError(f"外部服务失败: {obj.get('message')}")
        data_obj = obj.get('data') or {}
        base64_data = data_obj.get('image_base64')
        if not isinstance(base64_data, str) or not base64_data.strip():
            raise RuntimeError('外部服务未返回有效的 image_base64')
        base64_data = base64_data.strip()
        if base64_data.startswith('data:image'):
            base64_data = base64_data.split(',', 1)[-1]
        try:
            return base64.b64decode(base64_data)
        except Exception as e:
            raise RuntimeError(f'Base64解码失败: {e}')

    # 生成ZIP到内存
    zip_buffer = io.BytesIO()
    success_count = 0
    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for idx, html_str in enumerate(html_list, start=1):
            try:
                img_bytes = render_html_to_png_bytes(str(html_str))
                zipf.writestr(f'小红书图片_{idx}.png', img_bytes)
                success_count += 1
            except Exception as e:
                # 将失败信息写入ZIP，便于排查（不删除用户注释）
                zipf.writestr(f'error_{idx}.txt', f'生成第{idx}张图片失败: {str(e)}')

    if success_count == 0:
        return jsonify({
            'status': 'error',
            'message': '所有图片生成失败，请稍后重试'
        }), 502

    zip_buffer.seek(0)
    download_name = f"小红书图片集_{int(time.time() * 1000)}.zip"
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=download_name
    )