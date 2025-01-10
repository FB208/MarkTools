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

