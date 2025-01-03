import os
from flask import current_app as app
from flask import render_template, request, jsonify, Blueprint, Response, stream_with_context
from . import word_plugin_bp
from services.word_plugin_service import simple_chat as simple_chat_service, logic_vulnerability as logic_vulnerability_service, inspiration2outline, simple_optimize, super_expand
import json
from services.google_search_service import extract_search_keywords
from utils.google_search_util import GoogleSearchUtil
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.embeddings.embedding_v2_util import EmbeddingSearchV2 as EmbeddingSearch
from utils.embeddings.embedding_openai_faiss_util import OpenAIFaissUtil




@word_plugin_bp.route('/word_plugin/home')
def home():
    """单词插件页面"""

    return render_template('word_plugin/home.html')

# 简单优化
@word_plugin_bp.route('/word_plugin/simple_optimize')
def simple_optimize_stream():
    text = request.args.get('text', '')
    
    if not text:
        return {'error': '请提供文本内容'}, 400
    @stream_with_context
    def generate():
        try:
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '正在思考，请稍后。。。'}, ensure_ascii=False)}\n\n"
            
            optimize_content = simple_optimize(text)
            print("获取到优化内容:", optimize_content)  # 调试日志

            data = json.dumps({'step': 'optimize', 'message': optimize_content}, ensure_ascii=False)
           
            
            yield f"data: {data}\n\n"
            
            # 添加完成消息
            yield f"data: {json.dumps({'step': 'complete', 'content': '优化完成'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            print(f"Error in generate: {str(e)}")
            yield f"data: {json.dumps({'step': 'show_toast', 'content': f'发生错误: {str(e)}'}, ensure_ascii=False)}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )

# 超级扩写
@word_plugin_bp.route('/word_plugin/super_expand')
def super_expand_stream():
    text = request.args.get('text', '')
    
    if not text:
        return {'error': '请提供文本内容'}, 400
    
    def fetch_content(result, google_search_util):
        link = result['link']
        return google_search_util.fetch_page_content(link)
    def search_keyword(keyword, es):
        return es.search(keyword, top_k=3)

    @stream_with_context
    def generate():
        try:
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '正在思考，请稍后。。。'}, ensure_ascii=False)}\n\n"
            print("获取到扩写内容:", text)  # 调试日志
            # 提取搜索关键词
            keywords = extract_search_keywords(text)
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '正在从互联网搜索'}, ensure_ascii=False)}\n\n"
            google_search_util = GoogleSearchUtil()
            search_results = google_search_util.search(query=keywords,num_results=3)
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '正在处理搜索结果'}, ensure_ascii=False)}\n\n"
            
            # 使用线程池并发获取页面内容
            page_contents = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                # 提交所有任务，传入 google_search_util
                future_to_url = {executor.submit(fetch_content, result, google_search_util): result 
                               for result in search_results}
                
                # 获取完成的任务结果
                for future in as_completed(future_to_url):
                    page_result = future.result()
                    if page_result['status'] == 'success':
                        page_contents.append(page_result['content'])
            
            # 向量化，防止搜索结果过长
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '二次匹配搜索结果中最相关的内容'}, ensure_ascii=False)}\n\n"
            faiss_util = OpenAIFaissUtil()
            search_result_texts = []
            for content in page_contents:
                search_result_texts.extend(faiss_util.split_text(content,1000))
                
            embedding_search_results = []
            embedding_search_results = faiss_util.search_fast(
                query=keywords, 
                texts=search_result_texts, 
                top_k=3
            )
            print("embedding_search_results:", embedding_search_results)
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '正在润色文案'}, ensure_ascii=False)}\n\n"
            
            
            expand_content = super_expand(text, embedding_search_results)
            data = json.dumps({'step': 'content', 'message': expand_content}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            # expand_content = super_expand(text)
            # 添加完成消息
            yield f"data: {json.dumps({'step': 'complete', 'content': '优化完成'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            print(f"Error in generate: {str(e)}")
            yield f"data: {json.dumps({'step': 'show_toast', 'content': f'发生错误: {str(e)}'}, ensure_ascii=False)}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )

@word_plugin_bp.route('/word_plugin/simple_chat', methods=['POST'])
def simple_chat():
    text = request.json.get('text')
    result = simple_chat_service(text)
    return jsonify({'message': result})

# 排查逻辑漏洞
@word_plugin_bp.route('/word_plugin/logic_vulnerability', methods=['POST'])
def logic_vulnerability():
    text = request.json.get('text')
    
    # 将内容写入文件以查看完整内容
    base_path = os.path.join(app.config['BASE_PATH'], 'tempfiles','word_plugin')
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    with open(os.path.join(base_path, 'received_text.txt'), 'w', encoding='utf-8') as f:
        f.write(f"文本长度：{len(text)}\n")
        f.write("完整文本内容：\n")
        f.write(text)
    
    # 控制台输出长度信息
    print(f"接收到的文本长度：{len(text)} 字符")
    
    result = logic_vulnerability_service(text)
    return jsonify({'message': result})

@word_plugin_bp.route('/inspiration2outline_stream')
def inspiration2outline_stream():
    text = request.args.get('text', '')
    
    if not text:
        return {'error': '请提供文本内容'}, 400
    @stream_with_context
    def generate():
        try:
            yield f"data: {json.dumps({'step': 'show_toast', 'content': '开始生成提纲...'}, ensure_ascii=False)}\n\n"
            
            outline_content = inspiration2outline(text)
            print("获取到提纲内容:", outline_content)  # 调试日志
            
            data = json.dumps({'step': 'outline', 'message': outline_content}, ensure_ascii=False)
            print("准备发送数据:", data)  # 调试日志
            
            yield f"data: {data}\n\n"
            
            # 添加完成消息
            yield f"data: {json.dumps({'step': 'complete', 'content': '提纲生成完成'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            print(f"Error in generate: {str(e)}")
            yield f"data: {json.dumps({'step': 'show_toast', 'content': f'发生错误: {str(e)}'}, ensure_ascii=False)}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )
