from pydantic import Field

from ..base import FrigateBaseModel
from .topics import TopicsConfig

__all__ = ["LdConfig"]

class LdConfig(FrigateBaseModel):
    ip: str = Field(default="这里是树莓派的ip，用于调试是否成功", title="在这里输入树莓派的ip")
    enable: bool = Field(default=True, title="在这里输入树莓派是否启动")
    topics: TopicsConfig = Field(default_factory=TopicsConfig, title="在这里配置ld的topics")