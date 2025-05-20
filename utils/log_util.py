import os
import logging
import uuid
from datetime import datetime

# 确保日志目录存在
def ensure_log_dir():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

# 配置日志记录器
def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# 请求ID字典，用于关联同一请求的多条日志
_request_ids = {}

class LogUtil:
    def __init__(self):
        """初始化日志工具"""
        log_dir = ensure_log_dir()
        today = datetime.now().strftime('%Y-%m-%d')
        self.log_file = os.path.join(log_dir, f'llm_logs_{today}.log')
        self.logger = setup_logger('llm_logger', self.log_file)
    
    def _get_request_id(self):
        """获取当前线程的请求ID，如果不存在则创建一个"""
        import threading
        thread_id = threading.get_ident()
        if thread_id not in _request_ids:
            _request_ids[thread_id] = str(uuid.uuid4())[:8]  # 使用短UUID作为请求标识
        return _request_ids[thread_id]
    
    def _format_message(self, message):
        """格式化日志消息，添加请求ID和时间"""
        req_id = self._get_request_id()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f"[{req_id}] [{timestamp}] {message}"
    
    def info(self, message):
        """记录普通日志信息"""
        formatted_message = self._format_message(message)
        self.logger.info(formatted_message)
    
    def error(self, message):
        """记录错误日志信息"""
        formatted_message = self._format_message(message)
        self.logger.error(formatted_message)
    
    def set_request_id(self, req_id=None):
        """设置当前线程的请求ID"""
        import threading
        thread_id = threading.get_ident()
        if req_id is None:
            req_id = str(uuid.uuid4())[:8]
        _request_ids[thread_id] = req_id

# 创建一个单例实例
log = LogUtil() 