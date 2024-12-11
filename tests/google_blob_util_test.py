import pytest
import json
import os
from utils.google_blob_util import list_buckets
from app import create_app
from test_config import TestConfig

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

def test_list_buckets():
    with app.app_context():
        app.config['GOOGLE_CLOUD_PROJECT'] = TestConfig.GOOGLE_CLOUD_PROJECT
        os.environ['GOOGLE_CLOUD_PROJECT'] = TestConfig.GOOGLE_CLOUD_PROJECT
        result = list_buckets()
        print(result)
        assert False
        