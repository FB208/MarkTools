from mem0 import MemoryClient
from flask import current_app as app
# 文档地址https://docs.mem0.ai/platform/quickstart
# 更多高级方法可参照文档，直接get_instance()获取实例后调用

class Mem0AIClientSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            api_key = app.config['MEM0AI_API_KEY']
            cls._instance = MemoryClient(api_key=api_key)
        return cls._instance


def add(message, user_id):
    client = Mem0AIClientSingleton.get_instance()
    # 修改这里，将 message 和 user_id 作为关键字参数传递
    client.add(message, user_id=user_id)

def query(user_query,user_id):
    client = Mem0AIClientSingleton.get_instance()
    return client.search(user_query,user_id=user_id,output_format="v1.1")

def complex_query(user_query,filters):
    '''
query = "What do you know about me?"
filters = {
   "AND":[
      {
         "user_id":"alex"
      },
      {
         "agent_id":{
            "in":[
               "travel-assistant",
               "customer-support"
            ]
         }
      }
   ]
}
client.search(query, version="v2", filters=filters)

    '''
    client = Mem0AIClientSingleton.get_instance()
    return client.search(user_query, version="v2", filters=filters)

def list_user():
    client = Mem0AIClientSingleton.get_instance()
    return client.users()

# 获取用户的所有记忆
def get_all(user_id):
    client = Mem0AIClientSingleton.get_instance()
    return client.get_all(user_id=user_id,output_format="v1.1")

def update(memory_id,message):
    client = Mem0AIClientSingleton.get_instance()
    return client.update(memory_id,message)

def delete(memory_id):
    client = Mem0AIClientSingleton.get_instance()
    return client.delete(memory_id)

def delete_all(user_id):
    client = Mem0AIClientSingleton.get_instance()
    return client.delete_all(user_id=user_id)

