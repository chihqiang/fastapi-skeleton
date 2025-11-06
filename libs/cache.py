import os
import pickle
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

import redis
from redis import Redis
from redis.exceptions import RedisError

from config import setting
from libs.dicts import array_deep_merge


class CacheInterface(ABC):
    """缓存接口规范，定义通用缓存操作。"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        获取指定键的缓存值。

        :param key: 缓存键，非空字符串
        :return: 缓存值，键不存在/已过期/异常返回 None
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        """
        设置缓存值并指定过期时间。

        :param key: 缓存键，非空字符串
        :param value: 可序列化缓存值
        :param expire_seconds: 过期时间（秒），正整数，默认300秒
        :raises ValueError: 键为空或过期时间不合法
        :raises RuntimeError: 存储失败（如Redis连接异常）
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        删除指定缓存键。失败或不存在时静默处理。

        :param key: 缓存键，非空字符串
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        判断缓存键是否存在且未过期。

        :param key: 缓存键，非空字符串
        :return: True 表示键存在且有效，否则 False
        """
        pass


class RedisCache(CacheInterface):
    """基于 Redis 的缓存实现，支持多线程安全操作。"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 10,
        decode_responses: bool = False,
    ):
        """
        初始化 Redis 连接池。

        :param host: Redis 地址
        :param port: Redis 端口
        :param db: Redis 数据库编号
        :param password: Redis 密码
        :param max_connections: 连接池最大连接数
        :param decode_responses: 是否将返回字节自动解码为字符串
        """
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=decode_responses,
        )
        self._lock = threading.Lock()

    @property
    def _client(self) -> Redis:
        """获取 Redis 客户端实例（使用连接池）。"""
        return redis.Redis(connection_pool=self._pool)

    def get(self, key: str) -> Optional[Any]:
        if not isinstance(key, str) or not key.strip():
            return None
        with self._lock:
            try:
                return self._client.get(key)
            except RedisError:
                return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("键必须为非空字符串")
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("过期时间必须为正整数（秒）")
        with self._lock:
            try:
                self._client.set(key, value, ex=expire_seconds)
            except RedisError as e:
                raise RuntimeError(f"Redis 设置缓存失败（key: {key}）：{e}")

    def delete(self, key: str) -> None:
        if isinstance(key, str) and key.strip():
            with self._lock:
                try:
                    self._client.delete(key)
                except RedisError:
                    pass

    def exists(self, key: str) -> bool:
        if not isinstance(key, str) or not key.strip():
            return False
        with self._lock:
            try:
                return self._client.exists(key) == 1
            except RedisError:
                return False


class MemoryCache(CacheInterface):
    """基于内存的缓存实现，支持 LRU 淘汰策略。"""

    def __init__(self, max_size: int = 1000):
        """
        初始化内存缓存。

        :param max_size: 最大缓存数量，超过时触发 LRU 淘汰
        """
        self._cache: Dict[str, Tuple[Any, float, float]] = {}
        self._max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._cache.get(key)
            if not item:
                return None
            value, expire_ts, _ = item
            if time.time() > expire_ts:
                del self._cache[key]
                return None
            self._cache[key] = (value, expire_ts, time.time())
            return value

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("键必须为非空字符串")
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("过期时间必须为正整数（秒）")

        with self._lock:
            expire_ts = time.time() + expire_seconds
            self._cache[key] = (value, expire_ts, time.time())

            if len(self._cache) > self._max_size:
                sorted_keys = sorted(
                    self._cache.keys(), key=lambda k: self._cache[k][2]
                )
                evict_count = (
                    len(self._cache) - self._max_size + int(self._max_size * 0.1)
                )
                for k in sorted_keys[:evict_count]:
                    del self._cache[k]

    def delete(self, key: str) -> None:
        with self._lock:
            if isinstance(key, str) and key in self._cache:
                del self._cache[key]

    def exists(self, key: str) -> bool:
        with self._lock:
            item = self._cache.get(key)
            if not item:
                return False
            _, expire_ts, _ = item
            if time.time() > expire_ts:
                del self._cache[key]
                return False
            return True


class FileCache(CacheInterface):
    """基于文件的简单缓存实现，使用 pickle 序列化存储每个键。"""

    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.cache")

    def get(self, key: str) -> Optional[Any]:
        if not key:
            return None
        path = self._get_path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "rb") as f:
                expire_time, value = pickle.load(f)
            if expire_time is not None and time.time() > expire_time:
                try:
                    os.remove(path)
                except Exception:
                    pass
                return None
            return value
        except Exception:
            return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        if not key or not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("key不能为空，expire_seconds必须为正整数")
        path = self._get_path(key)
        expire_time = time.time() + expire_seconds
        try:
            with open(path, "wb") as f:
                pickle.dump((expire_time, value), f)
        except Exception as e:
            raise RuntimeError(f"写入缓存失败: {e}")

    def delete(self, key: str) -> None:
        if not key:
            return
        path = self._get_path(key)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    def exists(self, key: str) -> bool:
        if not key:
            return False
        path = self._get_path(key)
        if not os.path.exists(path):
            return False
        try:
            with open(path, "rb") as f:
                expire_time, _ = pickle.load(f)
            if expire_time is not None and time.time() > expire_time:
                try:
                    os.remove(path)
                except Exception:
                    pass
                return False
            return True
        except Exception:
            return False


class CacheFactory:
    """缓存工厂，根据配置创建缓存实例。"""

    SUPPORTED_CACHE_TYPE_MEMORY = "memory"
    SUPPORTED_CACHE_TYPE_REDIS = "redis"
    SUPPORTED_CACHE_TYPE_FILE = "file"

    SUPPORTED_CACHE_TYPES = [
        SUPPORTED_CACHE_TYPE_MEMORY,
        SUPPORTED_CACHE_TYPE_REDIS,
        SUPPORTED_CACHE_TYPE_FILE,
    ]

    DEFAULT_CONFIG = {
        "type": SUPPORTED_CACHE_TYPE_MEMORY,
        SUPPORTED_CACHE_TYPE_REDIS: {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None,
            "max_connections": 10,
            "decode_responses": False,
        },
        SUPPORTED_CACHE_TYPE_MEMORY: {"max_size": 1000},
        SUPPORTED_CACHE_TYPE_FILE: {"path": "storage/cache"},
    }

    @staticmethod
    def create_cache(user_config: dict = None) -> CacheInterface:
        """创建缓存实例，支持配置覆盖和默认值填充。"""
        config = CacheFactory.DEFAULT_CONFIG.copy()
        if user_config:
            config = array_deep_merge(config, user_config)

        current_type = config.get("type")
        if current_type not in CacheFactory.SUPPORTED_CACHE_TYPES:
            raise ValueError(
                f"不支持的缓存类型：{current_type}，仅支持 {CacheFactory.SUPPORTED_CACHE_TYPES}"
            )

        if current_type == CacheFactory.SUPPORTED_CACHE_TYPE_REDIS:
            return RedisCache(
                host=config.get("redis", {}).get("host"),
                port=config.get("redis", {}).get("port"),
                db=config.get("redis", {}).get("db"),
                password=config.get("redis", {}).get("password"),
                max_connections=config.get("redis", {}).get("max_connections"),
                decode_responses=config.get("redis", {}).get("decode_responses"),
            )
        elif current_type == CacheFactory.SUPPORTED_CACHE_TYPE_MEMORY:
            return MemoryCache(max_size=config.get("memory", {}).get("max_size"))
        elif current_type == CacheFactory.SUPPORTED_CACHE_TYPE_FILE:
            return FileCache(cache_dir=config.get("file", {}).get("path"))


# 默认缓存实例
_default_cache = CacheFactory.create_cache(setting.CACHE_CFG)
get = _default_cache.get
set = _default_cache.set
delete = _default_cache.delete
exists = _default_cache.exists
