import threading
from abc import ABC, abstractmethod
from enum import unique, Enum
from typing import Optional, Any, Dict, Tuple
import redis
from redis import Redis
from redis.exceptions import RedisError
import time

from config import setting


class CacheInterface(ABC):
    """缓存组件核心接口，定义通用缓存操作规范

    所有缓存实现类（如Redis缓存、内存缓存）需遵循此接口，
    保证业务代码对缓存操作的一致性和可替换性。
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        获取指定键的缓存值

        键不存在、已过期或发生异常时均返回None，业务层无需额外处理异常场景。

        :param key: 缓存键，必须为非空字符串（空字符串或None将直接返回None）
        :return: 缓存值（任意类型，取决于存储时的类型）；键不存在/过期/异常时返回None
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        """
        设置缓存键值对，支持自动过期

        键和过期时间会进行合法性校验，不合法时抛出ValueError；
        存储过程中发生异常（如Redis连接失败）时抛出RuntimeError。

        :param key: 缓存键，必须为非空字符串（空字符串将抛出异常）
        :param value: 缓存值，支持任意可序列化类型（具体取决于缓存实现）
        :param expire_seconds: 过期时间（秒），必须为正整数，默认300秒（5分钟）
        :raises ValueError: 当key为空字符串或expire_seconds非正整数时抛出
        :raises RuntimeError: 当存储操作发生异常（如连接失败）时抛出
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        删除指定缓存键

        无论键是否存在、删除是否成功，均不抛出异常（失败时静默处理），
        适合"确保键不存在"的场景。

        :param key: 缓存键，必须为非空字符串（空字符串将忽略操作）
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        检查键是否存在且未过期

        键不存在、已过期或发生异常时均返回False，仅在键有效存在时返回True。

        :param key: 缓存键，必须为非空字符串（空字符串将直接返回False）
        :return: 布尔值，True表示键存在且未过期，False表示不存在/已过期/异常
        """
        pass


class RedisCache(CacheInterface):
    """基于Redis的缓存实现，遵循CacheInterface接口规范

    依赖redis-py库实现与Redis服务器的交互，使用连接池管理连接，
    并通过线程锁保证多线程环境下的操作安全。
    """

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

        :param host: Redis服务器主机地址，默认localhost
        :param port: Redis服务器端口，默认6379
        :param db: 数据库编号（Redis支持多库，默认0）
        :param password: 连接Redis的认证密码，无密码则为None
        :param max_connections: 连接池最大连接数，控制并发量，默认10
        :param decode_responses: 是否自动将Redis返回的字节数据解码为字符串，
                                 默认False（返回字节类型）
        """
        # 初始化Redis连接池，避免频繁创建/关闭连接带来的性能损耗
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=decode_responses
        )
        self._lock = threading.Lock()  # 线程锁：保证多线程操作的原子性

    @property
    def _client(self) -> Redis:
        """从连接池获取Redis客户端实例

        每次调用均从连接池获取连接，使用完毕后自动归还，
        无需手动管理连接的创建和关闭。
        """
        return redis.Redis(connection_pool=self._pool)

    def get(self, key: str) -> Optional[Any]:
        # 键合法性校验：空字符串直接返回None
        if not isinstance(key, str) or not key.strip():
            return None

        # 加锁保证线程安全，避免多线程同时操作导致的连接混乱
        with self._lock:
            try:
                # 调用Redis的GET命令，返回值类型取决于decode_responses配置
                return self._client.get(key)
            except RedisError:
                # 捕获所有Redis相关异常（如连接失败、命令错误），返回None
                return None

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        # 键合法性校验：空字符串抛出异常
        if not isinstance(key, str) or not key.strip():
            raise ValueError("键必须为非空字符串（不能为空或仅含空白字符）")
        # 过期时间校验：必须为正整数
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("过期时间必须是正整数（秒），且大于0")

        with self._lock:
            try:
                # 调用Redis的SET命令，ex参数指定过期时间（秒）
                # Redis会自动处理值的序列化，支持字符串、数字、字节等类型
                self._client.set(key, value, ex=expire_seconds)
            except RedisError as e:
                # 捕获Redis异常（如连接失败），包装为RuntimeError抛出
                raise RuntimeError(f"Redis设置缓存失败（key: {key}）：{str(e)}")

    def delete(self, key: str) -> None:
        # 键合法性校验：空字符串忽略操作
        if isinstance(key, str) and key.strip():
            with self._lock:
                try:
                    # 调用Redis的DEL命令，删除指定键
                    # 即使键不存在，DEL命令也不会报错，因此无需提前检查
                    self._client.delete(key)
                except RedisError:
                    # 捕获异常并静默处理（删除失败不影响业务流程）
                    pass

    def exists(self, key: str) -> bool:
        # 键合法性校验：空字符串直接返回False
        if not isinstance(key, str) or not key.strip():
            return False

        with self._lock:
            try:
                # 调用Redis的EXISTS命令，返回1表示存在，0表示不存在
                # Redis会自动过滤已过期的键，因此返回True即表示键有效
                return self._client.exists(key) == 1
            except RedisError:
                # 捕获异常，返回False（视为键不存在）
                return False


class MemoryCache(CacheInterface):
    """基于内存的缓存实现，遵循CacheInterface接口规范

    适用于单进程场景，使用字典存储缓存数据，实现LRU（最近最少使用）淘汰策略，
    并通过线程锁保证多线程环境下的操作安全。
    """

    def __init__(self, max_size: int = 1000):
        """
        初始化内存缓存

        :param max_size: 缓存最大容量（键的数量），超出时触发LRU淘汰，默认1000
        """
        # 缓存存储结构：{key: (value, expire_ts, last_access_ts)}
        # value: 缓存值；expire_ts: 过期时间戳（秒）；last_access_ts: 最后访问时间戳（秒）
        self._cache: Dict[str, Tuple[Any, float, float]] = {}
        self._max_size = max_size  # 最大缓存数量，用于LRU淘汰
        self._lock = threading.Lock()  # 线程锁：保证多线程操作的原子性

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            # 尝试获取缓存项
            item = self._cache.get(key)
            if not item:
                return None  # 键不存在，返回None
            value, expire_ts, last_access_ts = item
            # 检查是否过期（当前时间 > 过期时间戳）
            if time.time() > expire_ts:
                del self._cache[key]  # 清理过期项
                return None
            # 更新最后访问时间戳（用于LRU淘汰策略）
            self._cache[key] = (value, expire_ts, time.time())
            return value

    def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        # 键合法性校验：空字符串抛出异常
        if not isinstance(key, str) or not key.strip():
            raise ValueError("键必须为非空字符串（不能为空或仅含空白字符）")
        # 过期时间校验：必须为正整数
        if not isinstance(expire_seconds, int) or expire_seconds <= 0:
            raise ValueError("过期时间必须是正整数（秒），且大于0")

        with self._lock:
            # 计算过期时间戳（当前时间 + 过期秒数）
            expire_ts = time.time() + expire_seconds
            # 存储缓存项，同时记录当前时间为最后访问时间
            self._cache[key] = (value, expire_ts, time.time())

            # 当缓存数量超出最大容量时，执行LRU淘汰
            if len(self._cache) > self._max_size:
                # 按最后访问时间戳升序排序（最久未使用的键排在前面）
                sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k][2])
                # 计算需要淘汰的数量：超出部分 + 10%预留空间（避免频繁触发淘汰）
                evict_count = len(self._cache) - self._max_size + int(self._max_size * 0.1)
                # 淘汰最久未使用的键
                for key_to_evict in sorted_keys[:evict_count]:
                    del self._cache[key_to_evict]

    def delete(self, key: str) -> None:
        with self._lock:
            # 仅当键存在时执行删除
            if isinstance(key, str) and key in self._cache:
                del self._cache[key]

    def exists(self, key: str) -> bool:
        with self._lock:
            # 尝试获取缓存项
            item = self._cache.get(key)
            if not item:
                return False  # 键不存在

            _, expire_ts, _ = item
            # 检查是否过期
            if time.time() > expire_ts:
                del self._cache[key]  # 清理过期项
                return False
            return True  # 键存在且未过期


class CacheFactory:
    # 支持的缓存类型（集中管理）
    SUPPORTED_CACHE_TYPES = ["memory", "redis"]
    """支持的缓存类型列表（字符串类型），新增类型需在此处添加"""

    # 默认配置（集中管理，所有场景共用一套默认值）
    DEFAULT_CONFIG = {
        "type": "memory",  # 默认使用内存缓存（无需外部依赖）
        # Redis缓存默认配置（仅当type为"redis"时生效）
        "redis": {
            "host": "localhost",  # Redis服务器地址（默认本地）
            "port": 6379,  # Redis默认端口
            "db": 0,  # Redis数据库编号（0-15）
            "password": None,  # 认证密码（默认无）
            "max_connections": 10,  # 连接池最大连接数
            "decode_responses": False  # 是否自动解码为字符串（默认字节）
        },
        # 内存缓存默认配置（仅当type为"memory"时生效）
        "memory": {
            "max_size": 1000  # 最大缓存容量（超出时LRU淘汰）
        }
    }
    """默认配置字典，所有未被用户覆盖的配置均使用此处值"""

    @staticmethod
    def create_cache(user_config: dict = None) -> CacheInterface:
        """
        创建缓存实例（基于字符串类型控制，支持配置覆盖与默认值填充）

        核心逻辑：
        1. 以 DEFAULT_CONFIG 为基础，合并用户传入的配置（仅覆盖存在的字段）
        2. 校验缓存类型是否在 SUPPORTED_CACHE_TYPES 中
        3. 根据最终配置创建对应类型的缓存实例

        :param user_config: 用户配置字典（可选），格式示例：
                           {
                               "type": "redis",  # 缓存类型（支持大小写）
                               "redis": {"host": "192.168.1.100"},  # Redis配置
                               "memory": {"max_size": 2000}  # 内存缓存配置
                           }
        :return: 缓存实例（RedisCache 或 MemoryCache）
        :raises ValueError: 当缓存类型不在支持列表中时抛出
        """
        # 复制默认配置作为基础（避免直接修改DEFAULT_CONFIG）
        config = CacheFactory.DEFAULT_CONFIG.copy()

        # 合并用户配置（仅覆盖存在的字段）
        if user_config:
            # 处理缓存类型：统一转为小写，兼容大小写输入
            if "type" in user_config:
                config["type"] = str(user_config["type"]).lower()

            # 覆盖Redis配置（仅处理默认配置中已有的字段）
            if "redis" in user_config and isinstance(user_config["redis"], dict):
                for key, value in user_config["redis"].items():
                    if key in config["redis"]:
                        config["redis"][key] = value

            # 覆盖内存缓存配置（仅处理默认配置中已有的字段）
            if "memory" in user_config and isinstance(user_config["memory"], dict):
                for key, value in user_config["memory"].items():
                    if key in config["memory"]:
                        config["memory"][key] = value

        # 校验缓存类型合法性
        current_type = config["type"]
        if current_type not in CacheFactory.SUPPORTED_CACHE_TYPES:
            raise ValueError(
                f"不支持的缓存类型：{current_type}，仅支持 {CacheFactory.SUPPORTED_CACHE_TYPES}"
            )

        # 创建对应类型的缓存实例
        if current_type == "redis":
            return RedisCache(
                host=config["redis"]["host"],
                port=config["redis"]["port"],
                db=config["redis"]["db"],
                password=config["redis"]["password"],
                max_connections=config["redis"]["max_connections"],
                decode_responses=config["redis"]["decode_responses"]
            )
        elif current_type == "memory":
            return MemoryCache(max_size=config["memory"]["max_size"])


_default_cache = CacheFactory.create_cache(setting.CACHE_CFG)
get = _default_cache.get
set = _default_cache.set
delete = _default_cache.delete
exists = _default_cache.exists
