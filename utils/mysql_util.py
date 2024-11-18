from peewee import *
from playhouse.db_url import connect
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库连接字符串
DATABASE_URL = os.getenv('MYSQL')

# 创建数据库连接池
db = connect(DATABASE_URL)

class MySQLUtil:
    """MySQL工具类"""
    
    @staticmethod
    def init_db():
        """初始化数据库连接"""
        if db.is_closed():
            db.connect()
    
    @staticmethod
    def close_db():
        """关闭数据库连接"""
        if not db.is_closed():
            db.close()
    
    @staticmethod
    def create_tables(models):
        """创建表"""
        with db:
            db.create_tables(models)
    
    @staticmethod
    def drop_tables(models):
        """删除表"""
        with db:
            db.drop_tables(models)
    
    @staticmethod
    def execute_sql(sql, params=None):
        """执行原生SQL"""
        return db.execute_sql(sql, params)

    @staticmethod
    def transaction():
        """事务装饰器"""
        return db.atomic()