from app import create_app
from test_config import TestConfig
from services.starbot_service import single_user_reply
from utils.redis_util import RedisUtil
from models.starbot_friend import StarbotFriend
from llm.llm_factory import LLMFactory

app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/service/starbot_service_test.py::test_simple_reply
def test_simple_reply():
    with app.app_context():
        result = single_user_reply("yanghuichao19930109", "吃午饭啦")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "我现在搬到杭州住了")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "帮我查下明天的天气吧")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "我是说查我现在居住的地方")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "你真的很博学多才啊")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "我才刚来不太清楚呢，最近有什么新闻吗")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "杭州近两天有民生相关的新闻吗")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "您谦虚了，我该多向你学习")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "哈哈，我们做好朋友吧")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "那你能介绍一下你自己吗")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "你有名字吗")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "我喜欢看电影，尤其是历史电影，你有什么爱好吗")
        #result = simple_reply("single_user","杨惠超", "杨惠超", "我最近在看《三国演义》，你看过吗")
        print(result)
        
# pytest -s tests/service/starbot_service_test.py::test_openai_json
def test_openai_json():
    with app.app_context():
        redis_util = RedisUtil()
        old_messages = redis_util.get_chat_history_except_recent('single_user', 'yanghuichao19930109', keep_recent=0)
        user = StarbotFriend.get_by_wx_id('yanghuichao19930109')
        current_summary = user.personality_summary
        system_message = """你是一个擅长总结聊天记录的人，擅长根据聊天记录总结出关键事件、人物关系和性格特点
        你将收到三组内容：
        1. 之前总结的摘要，用<OLD_SUMMARY>标签包裹
        2. 最近的聊天记录，用<NEW_CHAT_RECORD>标签包裹
        3. 之前总结的用户画像，用<BASE_INFO>标签包裹

        要求：
        1. 你将根据这两组内容，生成新的摘要和人物画像。
        2. 新的摘要应该包含之前总结的摘要和最近的聊天记录。
        3. 新的摘要应该简洁明了，不需要华丽的修饰，突出重点，不要超过500字。
        4. 人物画像要确保准确再更新,仔细剖析信息，提取出。
        5. 直接返回我要求的json对象，不要提供任何解释或文本。
        
        """
        user_prompt = f"""
        之前总结的摘要：<OLD_SUMMARY>{current_summary}</OLD_SUMMARY>
        最近的聊天记录：<NEW_CHAT_RECORD>{old_messages}</NEW_CHAT_RECORD>
        之前总结的用户画像：<BASE_INFO>{user.base_info}</BASE_INFO>
        """
        messages = [
            {"role": "developer", "content": f"{system_message}"},
            {"role": "user", "content": f"{user_prompt}"}
        ]
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "summary":{
                    "type":"string",
                    "description":"你新总结的摘要内容"
                },
                "user_profile":{
                    "type":"object",
                    "properties":{
                        "姓名":{
                            "type":"string",
                            "description":"姓名"
                        },
                        "性别":{
                            "type":"string",
                            "description":"性别"
                        },
                        "祖籍":{
                            "type":"string",
                            "description":"祖籍"
                        },
                        "现住址":{
                            "type":"string",
                            "description":"现住址"
                        },
                        "生日":{
                            "type":"string",
                            "description":"生日"
                        },
                        "职业":{
                            "type":"string",
                            "description":"职业"
                        },
                        "兴趣爱好":{
                            "type":"string",
                            "description":"兴趣爱好"
                        },
                        "简介":{
                            "type":"string",
                            "description":"简介"
                        }
                    }
                },
                "additionalProperties": True
            },
            "additionalProperties": True
        }

        llm_service = LLMFactory.get_llm_service("openai_proxy")
        completion = llm_service.get_json_completion_v2(messages,response_format)
        json_data = llm_service.get_messages(completion)
        print("json_data",json_data)
        

