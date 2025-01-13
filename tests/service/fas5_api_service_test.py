from app import create_app
from test_config import TestConfig
from services.fas5_api_service import FAS5APIService

app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/service/fas5_api_service_test.py::test_get_org_trees
def test_get_org_trees():
    with app.app_context():
        fas5_service = FAS5APIService()
        result = fas5_service.get_org_trees()
        print(result)
       
# pytest -s tests/service/fas5_api_service_test.py::test_get_device_alarm_messages_type_count
def test_get_device_alarm_messages_type_count():
    with app.app_context():
        fas5_service = FAS5APIService()
        result = fas5_service.get_device_alarm_messages_type_count("2024-11-01", "2024-11-30", "")
        print(result)

