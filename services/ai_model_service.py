import logging
from typing import Dict, List, Optional, Tuple

from config import Config
from models.ai_model import AIModel
from utils.mysql_util import MySQLUtil


class AIModelCache:
    """在内存中维护 ai_model 表的数据，便于全局快速访问"""

    _cache: List[Dict[str, Optional[str]]] = []
    _lookup: Dict[Tuple[str, str], Dict[str, Optional[str]]] = {}

    @classmethod
    def initialize(cls):
        """直接加载缓存（外部已确保表存在）"""
        cls.refresh_cache()

    @classmethod
    def refresh_cache(cls) -> List[Dict[str, Optional[str]]]:
        """从数据库重新加载缓存"""
        try:
            MySQLUtil.init_db()
            data: List[Dict[str, Optional[str]]] = []
            lookup: Dict[Tuple[str, str], Dict[str, Optional[str]]] = {}
            for item in AIModel.select():
                record = item.to_dict()
                data.append(record)
                key = cls._build_lookup_key(record['platform'], record['ai_type'])
                lookup[key] = record

            cls._cache = data
            cls._lookup = lookup
            return data
        except Exception as exc:
            logging.error("加载 ai_model 缓存失败: %s", exc)
            raise
        finally:
            MySQLUtil.close_db()

    @classmethod
    def get_all(cls) -> List[Dict[str, Optional[str]]]:
        """返回全部缓存数据"""
        return cls._cache

    @classmethod
    def get_by_type(cls, ai_type: Optional[str]) -> Optional[Dict[str, Optional[str]]]:
        """按用途获取当前平台的模型配置"""
        return cls.get_by_platform_and_type(cls._normalize_platform(None), ai_type)


    @classmethod
    def get_by_platform_and_type(cls, platform: Optional[str], ai_type: Optional[str]) -> Optional[Dict[str, Optional[str]]]:
        """按平台+用途获取对应配置，平台默认读取环境变量"""
        key = cls._build_lookup_key(platform, ai_type)
        return cls._lookup.get(key)


    @classmethod
    def _build_lookup_key(cls, platform: Optional[str], ai_type: Optional[str]) -> Tuple[str, str]:
        """构造缓存索引用的键"""
        safe_platform = cls._normalize_platform(platform)
        safe_type = (ai_type or '').strip().lower()
        return safe_platform, safe_type

    @staticmethod
    def _normalize_platform(platform: Optional[str]) -> str:
        """归一化平台名称，默认使用 Config.PLATFORM"""
        default_platform = getattr(Config, 'PLATFORM', '') or ''
        return (platform or default_platform).strip().lower()

