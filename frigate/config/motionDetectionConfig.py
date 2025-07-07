from pydantic import Field

from .base import FrigateBaseModel

__all__ = ["motionDetectionConfig"]


class motionDetectionConfig(FrigateBaseModel):
    enabled: bool = Field(default=False, description="是否开启运动检测")
