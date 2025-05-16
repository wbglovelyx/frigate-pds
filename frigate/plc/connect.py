import snap7
from snap7.util import set_bool


class SiemensPLCController:
    def __init__(self, ip: str, rack: int = 0, slot: int = 1):
        """
        初始化 PLC 控制器，连接到西门子 PLC。

        :param ip: PLC 的 IP 地址
        :param rack: 默认机架号，默认为 0
        :param slot: 默认插槽号，默认为 1
        """
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.client = snap7.client.Client()
        self.connect_statu = False
        self.connect_false_message = "连接失败，"

    def connect(self):
        """连接到 PLC"""
        try:
            self.client.connect(self.ip, self.rack, self.slot)
            self.connect_statu = True
        except Exception as e:
            self.connect_statu = False
            self.connect_false_message = "连接失败，" + str(e)

    def disconnect(self):
        """断开与 PLC 的连接"""
        self.client.disconnect()
        self.connect_statu = False

    def send_signals(self, signals: list[bool]):
        """
        发送信号到 PLC，最多同时发送两个信号。

        :param signals: 布尔类型的信号列表，最多包含两个信号
        """
        if len(signals) > 2:
            print("最多只能同时发送两个信号")
            return

        # 模拟向 PLC 发送信号（写入输出地址）
        for i, signal in enumerate(signals):
            # 每个信号写入不同的 DBX 地址，例如 DB1.DBX0.0, DB1.DBX0.1
            db_address = 1  # 数据块编号
            byte_offset = 0  # 字节偏移量
            bit_offset = i  # 设置不同的 bit 偏移量

            # 使用 snap7.util 的 set_bool 函数设置信号
            self.set_output_signal(db_address, byte_offset, bit_offset, signal)

        print("信号已成功发送。")

    def set_output_signal(self, db_address: int, byte_offset: int, bit_offset: int, value: bool):
        """
        向指定的数据块的地址设置一个布尔输出信号。

        :param db_address: 数据块地址
        :param byte_offset: 字节偏移
        :param bit_offset: 比特偏移
        :param value: 布尔值，True 为开，False 为关
        """
        try:
            # 获取当前数据块的内容
            db_data = self.client.read_area(snap7.types.Areas.DB, db_address, byte_offset, 1)

            # 设置特定位置的布尔值
            set_bool(db_data, 0, bit_offset, value)

            # 写回 PLC
            self.client.write_area(snap7.types.Areas.DB, db_address, byte_offset, db_data)
            print(f"成功写入信号到 DB{db_address}.DBX{byte_offset}.{bit_offset}，值: {value}")
        except Exception as e:
            print(f"写入信号失败: {e}")






# 示例：使用该类连接 PLC 并发送信号
if __name__ == "__main__":
    plc = SiemensPLCController(ip="192.168.0.1")
    plc.connect()

    # 发送两个信号
    plc.send_signals([True, False])  # 例如：设置 DB1.DBX0.0 为 True，DB1.DBX0.1 为 False

    # 断开连接
    plc.disconnect()
