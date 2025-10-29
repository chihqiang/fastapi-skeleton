import threading
from typing import Optional, Any
import redis
from redis import Redis
from redis.exceptions import RedisError


class RedisCache:
    """Redis 缓存管理器（支持任意可序列化类型值，线程安全封装）"""

    def __init__(
            self,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None,
            max_connections: int = 10,
            decode_responses: bool = False
    ):
        """
        初始化Redis缓存连接池

        :param host: Redis服务器主机地址
        :param port: Redis服务器端口
        :param db: 目标数据库编号（默认0）
        :param password: 连接认证密码（无密码则为None）
        :param max_connections: 连接池最大连接数（控制并发量）
        :param decode_responses: 是否自动将响应解码为字符串（默认False，返回字节）
        """
        # 初始化连接池，避免频繁创建/关闭连接
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=decode_responses
        )
        # 线程锁：保证多线程环境下单个操作的原子性（如避免get/set的竞态）
        self._lock = threading.Lock()

    @property
    def _client(self) -> Redis:
        """从连接池获取Redis客户端实例（每个操作自动获取/释放连接）"""
        return redis.Redis(connection_pool=self._pool)

    def get(self, key: str) -> Optional[Any]:
        """
        获取指定键的缓存值

        说明：
        - 键不存在或已过期时返回None
        - Redis会自动过滤过期键，无需客户端额外处理
        - 线程安全：通过锁保证操作原子性

        :param key: 缓存键（非空字符串）
        :return: 缓存值（Redis原生返回类型，字节或字符串），不存在则为None
        """
        if not isinstance(key, str) or not key.strip():
            return None

        with self._lock:
            try:
                return self._client.get(key)
            except RedisError:  # 捕获连接异常、命令错误等
                return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        """
        设置缓存键值对（带过期时间）

        说明：
        - 支持任意可被Redis序列化的类型（如字符串、数字、字节等）
        - 过期时间由Redis服务器维护，到期自动删除
        - 线程安全：通过锁避免并发set导致的覆盖顺序问题

        :param key: 缓存键（非空字符串）
        :param value: 缓存值（需支持Redis序列化）
        :param expire_seconds: 过期时间（秒，正整数，默认300秒）
        :return: 设置成功返回True，失败（含异常）返回False
        :raises ValueError: 键为空或过期时间非法时抛出
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("键必须为非空字符串")
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("过期时间必须是正整数（秒）")

        with self._lock:
            try:
                # ex参数指定过期时间（秒），set命令返回True表示成功
                return self._client.set(key, value, ex=expire_seconds)
            except RedisError:
                return False

    def delete(self, key: str) -> bool:
        """
        删除指定缓存键

        说明：
        - 键不存在时返回False
        - 线程安全：确保删除操作不会被其他线程中断

        :param key: 缓存键（非空字符串）
        :return: 删除成功（键存在且被删除）返回True，否则返回False
        """
        if not isinstance(key, str) or not key.strip():
            return False

        with self._lock:
            try:
                # delete命令返回被删除的键数量，>0表示成功
                return self._client.delete(key) > 0
            except RedisError:
                return False

    def exists(self, key: str) -> bool:
        """
        检查键是否存在且未过期

        说明：
        - Redis的exists命令会自动排除已过期的键
        - 线程安全：确保检查结果的即时性（不受其他线程并发修改影响）

        :param key: 缓存键（非空字符串）
        :return: 键存在且有效返回True，否则返回False
        """
        if not isinstance(key, str) or not key.strip():
            return False

        with self._lock:
            try:
                # exists命令返回1表示存在，0表示不存在
                return self._client.exists(key) == 1
            except RedisError:
                return False

    def clear_expired(self) -> int:
        """
        触发Redis清理过期键（主动触发，非必须）

        说明：
        - Redis默认会定期清理过期键（惰性删除+定期删除）
        - 此方法调用Redis的PEXPIRE命令相关机制，实际清理是异步的
        - 无法获取具体清理数量，返回0表示操作成功触发，-1表示失败

        :return: 0表示触发成功，-1表示操作失败
        """
        with self._lock:
            try:
                # 调用Redis的主动清理机制（非阻塞）
                self._client.execute_command("EVAL", "return redis.call('DBSIZE')", 0)
                return 0
            except RedisError:
                return -1

    def expire(self, key: str, expire_seconds: int) -> bool:
        """
        为已有键设置新的过期时间

        说明：
        - 若键不存在，返回False
        - 线程安全：确保过期时间设置的原子性

        :param key: 缓存键（非空字符串）
        :param expire_seconds: 新的过期时间（秒，正整数）
        :return: 设置成功返回True，否则返回False
        """
        if not isinstance(key, str) or not key.strip():
            return False
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            return False

        with self._lock:
            try:
                return self._client.expire(key, expire_seconds)
            except RedisError:
                return False

    def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间（秒）

        说明：
        - 返回值说明：
          - -2：键不存在
          - -1：键存在且永不过期
          - 正数：剩余过期时间（秒）
        - 线程安全：确保获取的时间是当前最新值

        :param key: 缓存键（非空字符串）
        :return: 剩余过期时间（秒），异常时返回-2
        """
        if not isinstance(key, str) or not key.strip():
            return -2

        with self._lock:
            try:
                return self._client.ttl(key)
            except RedisError:
                return -2


redis_cache = RedisCache(host="localhost", port=6379, db=0, max_connections=20)
get = redis_cache.get
set = redis_cache.set
delete = redis_cache.delete
exists = redis_cache.exists
clear_expired = redis_cache.clear_expired
expire = redis_cache.expire
ttl = redis_cache.ttl
