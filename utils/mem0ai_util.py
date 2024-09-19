from mem0 import MemoryClient
from flask import current_app as app

api_key = app.config['MEM0AI_API_KEY']


client = MemoryClient(api_key=api_key)
