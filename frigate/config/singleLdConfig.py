from pydantic import Field

from .base import FrigateBaseModel

__all__ = ["singleLdConfig"]


class singleLdConfig(FrigateBaseModel):
    enabled: bool = Field(default=False, description="是否单独使用雷达进行配置，而不是与摄像头串行")
    weight_2410b: float = Field(default=0.50, description="2410b的单独权重")
    weight_6002b: float = Field(default=0.40, description="6002b的单独权重")
    weight_red: float = Field(default=0.10, description="红外的单独权重")
    stop: float = Field(default=0.7, description="PLC停车阈值")
