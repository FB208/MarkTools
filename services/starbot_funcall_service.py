import json
import time
from llm.llm_factory import LLMFactory
from models.starbot_friend import StarbotFriend
from utils.redis_util import RedisUtil
import threading
from flask import current_app


#def function_call_fas5():
    