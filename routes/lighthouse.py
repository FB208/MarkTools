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
from models.s_keyword import SKeyword
from models.zy_history import ZyHistory
from utils.log_util import log
from datetime import datetime
from utils.text_util import convert_to_string
from flask_cors import CORS
# platform = 'grok'
# text_model = 'grok-3-mini-fast-beta'
# infer_model = 'grok-3-fast-beta'

wenan_platform = 'gemini'
wenan_model = 'gemini-2.5-flash-preview-05-20'
chaifen_platform = 'gemini'
chaifen_model = 'gemini-2.5-flash-preview-05-20'
kapian_platform = 'gemini'
kapian_model = 'gemini-2.5-flash-preview-05-20'
# wenan_platform = 'glm'
# wenan_model = 'glm-4-air'
# chaifen_platform = 'glm'
# chaifen_model = 'glm-4-air'
# kapian_platform = 'glm'
# kapian_model = 'glm-4-air'

platform = 'glm'
text_model = 'glm-4-air'
infer_model = 'glm-4-plus'
think_model = 'glm-z1-airx'

# platform = 'hsfz'
# text_model = 'deepseek-v3-250324'
# infer_model = 'deepseek-v3-250324'

CORS(app, resources={r"/lh/*": {"origins": "*"}}, max_age=3600)

@lighthouse_bp.route('/check_question', methods=['POST'])
def check_question():
    data = request.get_json()
    uuid = data.get('uuid', '')
    session[uuid] = data
    question = data.get('question', '')
    # 为当前请求设置一个UUID
    log.set_request_id(uuid)
    log.info(f"收到问题检查请求: {question}")
    
    # 这里可以添加处理逻辑,例如保存到数据库或开始后台任务
    messages = [
        {"role": "user", "content": lighthouse_prompt.check_question_prompt(question)}
    ]
    llm_service = LLMFactory.get_llm_service(platform)
    
    try:
        log.info(f"调用LLM服务 - 模型: {text_model}")
        completion = llm_service.get_chat_completion(model=text_model, messages=messages)
        result = llm_service.get_messages(completion)
        
        # 记录LLM调用结果
        log.info(f"LLM响应结果: {result}")
        
        ZyHistory.insert_record(uuid, 0, "user", question)
        # return jsonify({"success": True, "data": "OTHER", "message": "解析完成"})
        return jsonify({"success": True, "data": result, "message": "解析完成"})
    except Exception as e:
        # 记录错误信息
        log.error(f"LLM调用失败: {str(e)}")
        return jsonify({"success": False, "data": None, "message": f"解析失败: {str(e)}"})


@lighthouse_bp.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.get_json()
    uuid = data.get('uuid', '')
    question = data.get('question', '')
    numbers = data.get('numbers', [])
    
    # 为当前请求设置一个UUID
    log.set_request_id(uuid)
    log.info(f"收到问题分析请求: {question}, 数字: {numbers}")
    
    # 创建一个队列用于线程间通信
    result_queue = queue.Queue()
    
    def generate():
        try:
            # 计算基础卦辞
            gid, yid, bgid, attribute = lighthouse_service.analyze_numbers(numbers)
            log.info(f"传入数字数组: {str(numbers)} (长度: {len(numbers)})")
            log.info(f"计算卦象结果: 卦ID={gid}, 爻ID={yid}, 变卦ID={bgid}, 属性={attribute}")
            
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
                        completion = llm_service.get_chat_completion(model=think_model, messages=messages)
                        # json_str = llm_service.clear_thinking_msg(completion)
                        # json_result = json.loads(json_str)
                        # score = int(json_result['current']['score'])
                        # jixiong_levels = ["凶", "小凶", "中吉", "吉", "大吉"]
                        # jixiong = jixiong_levels[min(int(score // 20), 4)]
                        jixiong = llm_service.clear_thinking_msg(completion)
                        # 将结果放入队列
                        result_queue.put({"type": "jixiong", "status": "success", "content": jixiong})
                        all_messages += "吉凶分析:"+jixiong+"\n\n"
                except Exception as e:
                    result_queue.put({"type": "jixiong", "status": "error", "content": str(e)})
            
            @copy_current_request_context
            def suan_ji_xiong_postpose(jiegua, question):
                nonlocal all_messages
                # 使用应用上下文
                with app.app_context():
                    try:
                        messages = [
                            {"role": "user", "content": lighthouse_prompt.ask_jixiong_postpose_prompt(jiegua, question)}
                        ]
                        log.info(f"提示词: {messages}")
                        llm_service = LLMFactory.get_llm_service(platform)
                        completion = llm_service.get_json_completion(model=think_model, messages=messages)
                        json_str = llm_service.get_messages(completion)
                        log.info(f"吉凶分析结果: {json_str}")
                        json_result = json.loads(json_str)
                        score = int(json_result['score'])
                        jixiong = json_result['jixiong']
                        explanation = json_result['explanation']
                        jixiong_mapping = {
                            "大吉": "大吉",
                            "吉": "吉", 
                            "中平": "中吉",
                            "小凶": "小凶",
                            "大凶": "凶"
                        }
                        jixiong = jixiong_mapping.get(jixiong,"")
                        content = {
                            "jixiong": jixiong,
                            "content": f"""【{jixiong}】 卦象{score}分,{explanation}"""
                        }
                        all_messages += "吉凶分析:"+jixiong+"\n\n"
                        
                        return content
                    except Exception as e:
                        log.error(f"吉凶分析失败: {str(e)}")
                        return ""
            
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
                        completion = llm_service.get_chat_completion(model=think_model, messages=messages)
                        jiegua = llm_service.clear_thinking_msg(completion)
                        result_queue.put({"type": "jiegua", "status": "success", "content": jiegua})
                        all_messages += "解卦分析:"+jiegua+"\n\n"
                except Exception as e:
                    result_queue.put({"type": "jiegua", "status": "error", "content": str(e)})
            @copy_current_request_context
            def jie_gua_front(gua_info, yao_bian_info, bi_gua_info, question):
                nonlocal all_messages
                # 使用应用上下文
                with app.app_context():
                    messages = [
                        {"role": "system", "content": lighthouse_prompt.system_prompt()},
                        {"role": "user", "content": lighthouse_prompt.ask_jiegua_prompt(gua_info, yao_bian_info, bi_gua_info, question)}
                    ]
                    log.info(f"前置解卦提示词: {messages}")
                    llm_service = LLMFactory.get_llm_service(platform)
                    completion = llm_service.get_chat_completion(model=think_model, messages=messages)
                    jiegua = llm_service.clear_thinking_msg(completion)
                    all_messages += "解卦分析:"+jiegua+"\n\n"
                    log.info(f"前置解卦结果: {jiegua}")
                    return jiegua
            try:
                result_jiegua = jie_gua_front(gua_info, yao_bian_info, bi_gua_info, question)
                yield f"data: {json.dumps({'type': 'jiegua', 'status': 'success', 'content': result_jiegua})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'jiegua', 'status': 'error', 'content': str(e)})}\n\n"
            try:
                result_jixiong = suan_ji_xiong_postpose(result_jiegua, question)
                yield f"data: {json.dumps({'type': 'jixiong', 'status': 'success', 'content': result_jixiong})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'jixiong', 'status': 'error', 'content': str(e)})}\n\n"

            # # 启动线程计算吉凶
            # thread_suan_ji_xiong = threading.Thread(
            #     target=suan_ji_xiong,
            #     args=(gua_info.gy_name, yao_bian_info.gy_name, bi_gua_info.gy_name, question, result_queue),
            #     daemon=True
            # )
            
            # # 启动线程解卦
            # thread_jie_gua = threading.Thread(
            #     target=jie_gua,
            #     args=(gua_info, yao_bian_info, bi_gua_info, question, result_queue),
            #     daemon=True
            # )
            
            # # 启动两个线程
            # thread_suan_ji_xiong.start()
            # thread_jie_gua.start()
            
            # # 跟踪两个任务的状态
            # tasks_status = {
            #     "jixiong": False,  # 吉凶任务是否完成
            #     "jiegua": False    # 解卦任务是否完成
            # }
            
            # # 等待两个线程完成并发送结果
            # while not (tasks_status["jixiong"] and tasks_status["jiegua"]):
            #     try:
            #         # 使用非阻塞方式从队列获取结果,设置超时时间为0.5秒
            #         result = result_queue.get(timeout=0.5)
            #         result_type = result.get("type")
            #         status = result.get("status")
            #         content = result.get("content")
                    
            #         # 更新任务状态
            #         if result_type in tasks_status:
            #             tasks_status[result_type] = True
                    
            #         # 发送结果到前端
            #         yield f"data: {json.dumps({'type': result_type, 'status': status, 'content': content})}\n\n"
                    
            #     except queue.Empty:
            #         # 队列为空时,继续等待
            #         continue
            #     except Exception as e:
            #         # 处理其他异常
            #         yield f"data: {json.dumps({'type': 'error', 'status': 'error', 'content': str(e)})}\n\n"
            
            # # 检查线程是否仍然活跃
            # if thread_suan_ji_xiong.is_alive():
            #     thread_suan_ji_xiong.join(timeout=1.0)
            # if thread_jie_gua.is_alive():
            #     thread_jie_gua.join(timeout=1.0)
            ZyHistory.insert_record(uuid, 0, "assistant", all_messages)
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '解析完成'})}\n\n"
            
        except Exception as e:
            log.error(f"处理过程中出现异常: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'status': 'error', 'content': str(e)})}\n\n"
            # 确保在异常情况下也发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '解析完成'})}\n\n"
            
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


    
@lighthouse_bp.route('/follow_ask_question', methods=['POST'])
def follow_ask_question():
    # 获取请求数据
    data = request.get_json()
    uuid = data.get('uuid', '')
    question = data.get('question', '')
    
    historys = ZyHistory.get_by_chat_id(uuid)
    if historys.count() >=12:
        return jsonify({"success": True, "data": "已超过5次追问,请点击【重新开始】,换个角度重新提问", "message": "已超过5次追问,请点击“重新开始”,换个角度重新提问"})
    messages = [
        {"role": "system", "content": lighthouse_prompt.system_prompt()}
    ]
    for item in historys:
        messages.append({"role": item.role, "content": item.content})

    prompt = lighthouse_prompt.follow_ask_question_prompt(question)
    messages.append({"role": "user", "content": prompt})
    log.info(f"追问提示词: {messages}")
    llm_service = LLMFactory.get_llm_service(platform)
    completion = llm_service.get_chat_completion(model=think_model, messages=messages)
    result = llm_service.clear_thinking_msg(completion)
    ZyHistory.insert_record(uuid, 0, "user", question)
    ZyHistory.insert_record(uuid, 0, "assistant", result)
    
    log.info(f"追问结果: {result}")
    return jsonify({"success": True, "data": result, "message": "解析完成"})

@lighthouse_bp.route('/generate_redbook', methods=['POST'])
def generate_redbook():
    data = request.get_json()
    uuid = data.get('uuid', '')
    
    def get_chat_history(uuid):
        historys = ZyHistory.get_by_chat_id(uuid)
        messages = []
        for item in historys:
            messages.append({"role": item.role, "content": item.content})
        return messages
    
    def get_wen_an(chat_history):
        system_prompt = """
你是一个小红书文案专家,擅长用创造性的天赋生成小红书文案。

用户发来的数据是基于易经算卦解卦的对话数据,你需要结合对话数据,生成一篇小红书文案（内容精简、易读的格式、吸引力的标题、善用emoji）。
标题处要体现易经,如：“易经如何看待俄乌停火谈判？”、“用易经解读2025年运势”等。
文案长度要适中,有较好的阅读体验。



仅返回生成的文案,不要包含任何其他内容。
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(chat_history)}
        ]
        llm_service = LLMFactory.get_llm_service(wenan_platform)
        completion = llm_service.get_chat_completion(model=wenan_model, messages=messages)
        wenan = llm_service.clear_thinking_msg(completion)
        return wenan
    
    def chaifen_wenan(wenan):
        from pydantic import BaseModel
        json_schema = {
            "data":[]
        }
        class Schema(BaseModel):
            data: list[str]
        system_prompt = f"""
你是一个小红书运营达人,也非常懂得人工智能的使用。

用户需要用AI来生成卡片形式的图片,以用于小红书文案的配图,不需要带井号标签。。

你的任务是基于用户发来对话内容,总结并拆分成4段内容,包括一个首页卡片,和3个内容卡片。

如果有和日期相关的内容,你要清楚当前时间是{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。

以文本介绍的形式体现。

将4段文本介绍拼接成json对象,参考格式如下：
{json_schema}
直接返回json对象,不要包含任何其他内容。
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": wenan}
        ]
        llm_service = LLMFactory.get_llm_service(chaifen_platform)
        completion = llm_service.get_json_completion(model=chaifen_model, messages=messages)
        chaifen = llm_service.get_messages(completion)
        json_result = json.loads(chaifen)
        return json_result['data']

    def generate():
        # 立即发送一个心跳数据,保持连接活跃
        yield f"data: {json.dumps({'type': 'heartbeat', 'status': 'success', 'content': '连接已建立'})}\n\n"
        
        chat_history = get_chat_history(uuid)
        wenan = get_wen_an(chat_history)
        yield f"data: {json.dumps({'type': 'text', 'status': 'success', 'content': wenan})}\n\n"
        chaifen = chaifen_wenan(wenan)
        
        # for index,chaifen_content in enumerate(chaifen):
        #     kapian_html = generate_kapian(index,chaifen_content,chat_history)
        #     yield f"data: {json.dumps({'type': f'pic', 'status': 'success', 'content': kapian_html})}\n\n"
        result_queue = queue.Queue()
        @copy_current_request_context
        def generate_kapian(index,chaifen_content,chat_history,result_queue):
            with app.app_context():
                first_kapian_prompt = f"""你正在生成的是小红书封面图,标题一定要用较大的字(为防止字体设置不生效,要加上!important属性),标题居中显示,标题字数多存在换行的情况,你需要在合适的位置增加换行符,而不是让它超过宽度自动换行。
                
                封面总文字数量要少,你可以忽略你认为不重要的内容。
                
                生成的卡片要有让人阅读的欲望
                """
                system_prompt = f"""
                根据用户提供的内容生成适合小红书发布的图片,内容的尺寸固定位宽600px,高800px。

                你可以使用html+css+svg+canvas来实现类似图片的效果,固定宽高比3:4。

                注意图片要非常美观,乐观向上的主题配色,给人舒适和高端的感觉,吸引人阅读,适合用于小红书文案的配图。

                内容包含渐变色、小图标和丰富的背景元素。

                你生成的内容最终会以图片的形式展示,所以不需要js和动画效果,也不要出现滚动条和任何指引交互的内容,你可以适当调整文案以确保内容高度控制在800px以内。
                
                {index == 0 and first_kapian_prompt or ""}

                不要使用markdown,直接返回div,使用行内css,不需要外层的html。
                """
                #                 整篇小红书的内容是基于以下对话生成的,你要做的是生成其中的一张配图,本张图片的内容用户会发给你。
                # {json.dumps(chat_history)}
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chaifen_content}
                ]
                llm_service = LLMFactory.get_llm_service(kapian_platform)
                completion = llm_service.get_chat_completion(model=kapian_model, messages=messages)
                kapian = llm_service.clear_thinking_msg(completion)
                kapian_html = kapian.replace('```html', '').replace('```', '').strip()
                kapian_html = convert_to_string(kapian_html)
                log.info(f"生成卡片: {kapian_html}")
                result_queue.put(kapian_html)
                # return kapian_html
        # 创建线程列表
        threads = []
        for index,chaifen_content in enumerate(chaifen):
            thread_kapian = threading.Thread(
                target=generate_kapian,
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
        yield f"data: {json.dumps({'type': 'done', 'status': 'success', 'content': '生成完成'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')