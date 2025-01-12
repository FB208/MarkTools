from app import create_app
from test_config import TestConfig
from services.starbot_api_service import StarBotAPIService

app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/service/starbot_api_service_test.py::test_get_account_list
def test_get_account_list():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.get_account_list()
        print(result)
       
# pytest -s tests/service/starbot_api_service_test.py::test_get_robot_info
def test_get_robot_info():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.get_robot_info()
        print(result)
         
# pytest -s tests/service/starbot_api_service_test.py::test_get_group_list
def test_get_group_list():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.get_group_list()
        print(result)

# pytest -s tests/service/starbot_api_service_test.py::test_get_friend_list
def test_get_friend_list():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.get_friend_list()
        print(result)

# pytest -s tests/service/starbot_api_service_test.py::test_query_friend_or_group_info
def test_query_friend_or_group_info():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.query_friend_or_group_info('yanghuichao19930109')
        print(result)

# pytest -s tests/service/starbot_api_service_test.py::test_send_text_message
def test_send_text_message():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.send_text_message('wxid_ct502916lbtq22', 'yanghuichao19930109', '666 666')
        print(result)

# pytest -s tests/service/starbot_api_service_test.py::test_send_text_message_to_group
def test_send_text_message_to_group():
    with app.app_context():
        starbot_service = StarBotAPIService()
        result = starbot_service.send_text_message('wxid_ct502916lbtq22', '13887961909@chatroom', '[@,wxid=\"yanghuichao19930109\",nick=,isAuto=true] 666 666 ')
        print(result)