from app import create_app
from test_config import TestConfig
from services.starbot_service import single_user_reply

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
        


