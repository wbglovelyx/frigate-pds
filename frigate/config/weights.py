from pydantic import Field

from .base import FrigateBaseModel

__all__ = ["WeightsConfig"]


class WeightsConfig(FrigateBaseModel):
    red: float = Field(default=0.00, title="这里用于指定red的权重")
    ld2410b: float = Field(default=0.00, title="这里用于指定ld2410b的权重")
    ld6002b: float = Field(default=0.00, title="这里用于指定ld6002b的权重")
    camera: float = Field(default=0.00, title="这里用于指定camera的权重")
    slow: float = Field(default=0.00, title="这里用于指定减速的权重")
    stop: float = Field(default=0.00, title="这里用于指定停车的权重")