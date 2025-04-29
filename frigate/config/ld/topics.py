
from pydantic import Field

from ..base import FrigateBaseModel

__all__ = ["TopicsConfig"]


class TopicsConfig(FrigateBaseModel):
    red: str = Field(default="这是是示例red主题名，用于调试是否成功",title="此处填入red的topic")
    red_queue_length: int = Field(default=5, title="规定一下red接收几个值开始判断")

    ld2410b: str = Field(default="这是是示例ld2410b主题名，用于调试是否成功",title="此处填入ld2410b的topic")
    ld2410b_queue_length: int = Field(default=5, title="规定一下ld2410b接收几个值开始判断")

    ld6002b: str = Field(default="这是是示例ld6002b主题名，用于调试是否成功",title="此处填入ld6002b的topic")
    ld6002b_queue_length: int = Field(default=5, title="规定一下ld6002b接收几个值开始判断")

    info_data: str = Field(default="这是是示例ld状态主题名，用于调试是否成功",title="此处填入info_data的topic")
