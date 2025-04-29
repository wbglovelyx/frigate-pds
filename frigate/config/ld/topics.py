
from pydantic import Field

from ..base import FrigateBaseModel

__all__ = ["TopicsConfig"]


class TopicsConfig(FrigateBaseModel):
    red: str = Field(default="这是是示例red主题名，用于调试是否成功",title="此处填入red的topic")
    ld2410b: str = Field(default="这是是示例ld2410b主题名，用于调试是否成功",title="此处填入ld2410b的topic")
    ld6002b: str = Field(default="这是是示例ld6002b主题名，用于调试是否成功",title="此处填入ld6002b的topic")
    info_data: str = Field(default="这是是示例ld状态主题名，用于调试是否成功",title="此处填入info_data的topic")
