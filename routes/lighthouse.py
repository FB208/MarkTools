from flask import current_app as app, copy_current_request_context, stream_with_context
from flask import render_template, request, jsonify, Response, session
import json
import time
from . import lighthouse_bp
from prompts import lighthouse_prompt
from llm.llm_factory import LLMFactory
from services import lighthouse_service
from models.zy_gy import ZyGy
import threading
import queue
from models.zy_history import ZyHistory

platform = 'grok'
text_model = 'grok-3-mini-fast-beta'
infer_model = 'grok-3-fast-beta'

# platform = 'glm'
# text_model = 'glm-4-air'
# infer_model = 'glm-4'

@lighthouse_bp.route('/check_question', methods=['POST'])
def check_question():
    data = request.get_json()
    uuid = data.get('uuid', '')
    session[uuid] = data
    
    # print(f"接收到的内容: {content}")
    # print(f"是否需要翻译: {translate}")
    
    # 这里可以添加处理逻辑，例如保存到数据库或开始后台任务
    messages = [
        {"role": "user", "content": lighthouse_prompt.check_question_prompt(data.get('question', ''))}
    ]
    llm_service = LLMFactory.get_llm_service(platform)
    completion = llm_service.get_chat_completion(model=text_model, messages=messages)
    result = llm_service.get_messages(completion)
    ZyHistory.insert_record(uuid, 0, "user", data.get('question', ''))
    return jsonify({"success": True, "data": result, "message": "解析完成"})


@lighthouse_bp.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.get_json()
    uuid = data.get('uuid', '')
    question = data.get('question', '')
    numbers = data.get('numbers', [])
    
    # 创建一个队列用于线程间通信
    result_queue = queue.Queue()
    
    def generate():
        try:
            # 计算基础卦辞
            gid, yid, bgid, attribute = lighthouse_service.analyze_numbers(numbers)
            
            # 在主线程中获取数据库数据
            gua_info = ZyGy.get_by_id(gid)
            yao_bian_info = ZyGy.get_by_id(yid)
            bi_gua_info = ZyGy.get_by_id(bgid)
            
            all_messages = ''
            
            content_base = f"""【{attribute}{gua_info.gy_name}({lighthouse_service.get_64gua_ico(gua_info.gy_sort-1)})】{gua_info.gy_content}
【{yao_bian_info.gy_name}爻】{yao_bian_info.gy_content}
【变{bi_gua_info.gy_name}({lighthouse_service.get_64gua_ico(bi_gua_info.gy_sort-1)})】{bi_gua_info.gy_content}"""
            all_messages += content_base+"\n\n"
            # 发送基础卦辞信息
            yield f"data: {json.dumps({'type': 'base', 'status': 'success', 'content': content_base})}\n\n"
            
            # 使用copy_current_request_context装饰器保持请求上下文
            @copy_current_request_context
            def suan_ji_xiong(bengua, yaobian, biangua, question, result_queue):
                nonlocal all_messages
                try:
                    # 使用应用上下文
                    with app.app_context():
                        messages = [
                            {"role": "user", "content": lighthouse_prompt.ask_jixiong_prompt(bengua, yaobian, biangua, question)}
                        ]
                        llm_service = LLMFactory.get_llm_service(platform)
                        completion = llm_service.get_json_completion(model=infer_model, messages=messages)
                        json_str = llm_service.get_messages(completion)
                        json_result = json.loads(json_str)
                        score = int(json_result['current']['score'])
                        jixiong_levels = ["凶", "小凶", "中吉", "吉", "大吉"]
                        jixiong = jixiong_levels[min(int(score // 20), 4)]
                        # 将结果放入队列
                        result_queue.put({"type": "jixiong", "status": "success", "content": jixiong})
                        all_messages += "吉凶分析："+jixiong+"\n\n"
                except Exception as e:
                    result_queue.put({"type": "jixiong", "status": "error", "content": str(e)})
            
            # 使用copy_current_request_context装饰器保持请求上下文
            @copy_current_request_context
            def jie_gua(gua_info, yao_bian_info, bi_gua_info, question, result_queue):
                nonlocal all_messages
                try:
                    # 使用应用上下文
                    with app.app_context():
                        messages = [
                            {"role": "user", "content": lighthouse_prompt.ask_jiegua_prompt(gua_info, yao_bian_info, bi_gua_info, question)}
                        ]
                        llm_service = LLMFactory.get_llm_service(platform)
                        completion = llm_service.get_chat_completion(model=infer_model, messages=messages)
                        jiegua = llm_service.get_messages(completion)
                        result_queue.put({"type": "jiegua", "status": "success", "content": jiegua})
                        all_messages += "解卦分析："+jiegua+"\n\n"
                except Exception as e:
                    result_queue.put({"type": "jiegua", "status": "error", "content": str(e)})
            
            # 启动线程计算吉凶
            thread_suan_ji_xiong = threading.Thread(
                target=suan_ji_xiong,
                args=(gua_info.gy_name, yao_bian_info.gy_name, bi_gua_info.gy_name, question, result_queue),
                daemon=True
            )
            
            # 启动线程解卦
            thread_jie_gua = threading.Thread(
                target=jie_gua,
                args=(gua_info, yao_bian_info, bi_gua_info, question, result_queue),
                daemon=True
            )
            
            # 启动两个线程
            thread_suan_ji_xiong.start()
            thread_jie_gua.start()
            
            # 跟踪两个任务的状态
            tasks_status = {
                "jixiong": False,  # 吉凶任务是否完成
                "jiegua": False    # 解卦任务是否完成
            }
            
            # 等待两个线程完成并发送结果
            while not (tasks_status["jixiong"] and tasks_status["jiegua"]):
                try:
                    # 使用非阻塞方式从队列获取结果，设置超时时间为0.5秒
                    result = result_queue.get(timeout=0.5)
                    result_type = result.get("type")
                    status = result.get("status")
                    content = result.get("content")
                    
                    # 更新任务状态
                    if result_type in tasks_status:
                        tasks_status[result_type] = True
                    
                    # 发送结果到前端
                    yield f"data: {json.dumps({'type': result_type, 'status': status, 'content': content})}\n\n"
                    
                except queue.Empty:
                    # 队列为空时，继续等待
                    continue
                except Exception as e:
                    # 处理其他异常
                    yield f"data: {json.dumps({'type': 'error', 'status': 'error', 'content': str(e)})}\n\n"
            
            # 检查线程是否仍然活跃
            if thread_suan_ji_xiong.is_alive():
                thread_suan_ji_xiong.join(timeout=1.0)
            if thread_jie_gua.is_alive():
                thread_jie_gua.join(timeout=1.0)
            ZyHistory.insert_record(uuid, 0, "assistant", all_messages)
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '解析完成'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'status': 'error', 'content': str(e)})}\n\n"
            # 确保在异常情况下也发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '解析完成'})}\n\n"
            
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


    
@lighthouse_bp.route('/follow_ask_question', methods=['POST'])
def follow_ask_question():
    data = request.get_json()
    uuid = data.get('uuid', '')
    question = data.get('question', '')
    
    historys = ZyHistory.get_by_chat_id(uuid)
    if historys.count() >=12:
        return jsonify({"success": True, "data": "已超过5次追问，请点击“重新开始”，换个角度重新提问", "message": "已超过5次追问，请点击“重新开始”，换个角度重新提问"})
    messages = []
    for item in historys:
        messages.append({"role": item.role, "content": item.content})

    prompt = lighthouse_prompt.follow_ask_question_prompt(question)
    messages.append({"role": "user", "content": prompt})
    
    llm_service = LLMFactory.get_llm_service(platform)
    completion = llm_service.get_chat_completion(model=infer_model, messages=messages)
    result = llm_service.get_messages(completion)
    ZyHistory.insert_record(uuid, 0, "user", question)
    ZyHistory.insert_record(uuid, 0, "assistant", result)
    return jsonify({"success": True, "data": result, "message": "解析完成"})
