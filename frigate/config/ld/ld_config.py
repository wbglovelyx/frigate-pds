from pydantic import Field

from ..base import FrigateBaseModel
from .topics import TopicsConfig

__all__ = ["LdConfig"]

class LdConfig(FrigateBaseModel):
    ip: str = Field(default="192.168.0.45", title="在这里输入树莓派的ip")
    port: int = Field(default=1883, title="这里用于输入端口号")
    username: str = Field(default="first", title="这里输入mqtt的用户名称")
    password: str = Field(default="123", title="这里输入mqtt的用户密码")
    enable: bool = Field(default=True, title="在这里输入树莓派是否启动")
    topics: TopicsConfig = Field(default_factory=TopicsConfig, title="在这里配置ld的topics")