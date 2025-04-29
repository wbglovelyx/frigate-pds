from pydantic import Field

from .base import FrigateBaseModel

__all__ = ["PlcConfig"]


class PlcConfig(FrigateBaseModel):
    name: str = Field(default="这是示例plc，用于调试是否读取成功", title="这里用于指定plc的名称")
    ip: str = Field(default="这是示例ip地址，用于调试是否读取成功", title="这里用于指定plc的ip地址")
    enable: bool = Field(default=False, title="这里用于指定是否启用plc")