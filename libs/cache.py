import time
import threading
from typing import Optional, Tuple, Dict, Any


class MemoryCache:
    """通用内存缓存管理器（支持任意类型值，线程安全 + LRU 淘汰）"""

    def __init__(self, max_size: int = 1000):
        # 缓存结构：{key: (value, expire_ts, last_access_ts)}
        # value: 任意类型；expire_ts: 过期时间戳；last_access_ts: 最后访问时间戳
        self._cache: Dict[str, Tuple[Any, float, float]] = {}
        self._max_size = max_size  # 最大缓存数量
        self._lock = threading.Lock()  # 线程锁保证并发安全

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值（自动检查过期，更新访问时间）"""
        with self._lock:
            item = self._cache.get(key)
            if not item:
                return None  # 键不存在

            value, expire_ts, last_access_ts = item

            # 检查是否过期
            if time.time() > expire_ts:
                del self._cache[key]
                return None  # 已过期

            # 更新最后访问时间（用于 LRU 淘汰）
            self._cache[key] = (value, expire_ts, time.time())
            return value

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        """设置缓存值（支持任意类型，自动淘汰淘汰超龄项）"""
        if not isinstance(key, str) or not key.strip():
            raise ValueError("键不能为空字符串")
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("有效期必须是正整数（秒）")

        expire_ts = time.time() + expire_seconds
        current_time = time.time()

        with self._lock:
            # 存储值（支持任意类型）、过期时间、最后访问时间
            self._cache[key] = (value, expire_ts, current_time)

            # LRU 淘汰：超出最大容量时，删除最久未使用的项
            if len(self._cache) > self._max_size:
                # 按最后访问时间排序，取最旧的一批删除
                sorted_keys = sorted(
                    self._cache.keys(),
                    key=lambda k: self._cache[k][2]  # 按 last_access_ts 升序
                )
                # 淘汰数量：超出部分 + 10% 预留空间
                evict_count = len(self._cache) - self._max_size + int(self._max_size * 0.1)
                for key_to_evict in sorted_keys[:evict_count]:
                    del self._cache[key_to_evict]

    def delete(self, key: str) -> None:
        """删除指定键的缓存"""
        with self._lock:
            if isinstance(key, str) and key in self._cache:
                del self._cache[key]

    def exists(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        with self._lock:
            item = self._cache.get(key)
            if not item:
                return False

            _, expire_ts, _ = item
            if time.time() > expire_ts:
                del self._cache[key]  # 清理过期项
                return False
            return True

    def clear_expired(self) -> None:
        """批量所有过期缓存"""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, (_, expire_ts, _) in self._cache.items()
                if current_time > expire_ts
            ]
            for key in expired_keys:
                del self._cache[key]


# 单例实例（全局共享）
cache = MemoryCache(max_size=1000)
# 对外暴露的简化接口
get = cache.get
set = cache.set
delete = cache.delete
exists = cache.exists
clear_expired = cache.clear_expired
