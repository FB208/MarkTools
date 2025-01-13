import json
import time
from llm.llm_factory import LLMFactory
from utils.mem0ai_util import query as mem0ai_query,add as mem0ai_add
from models.starbot_friend import StarbotFriend
from utils.redis_util import RedisUtil
import threading
from flask import current_app


#def function_call_fas5():
    