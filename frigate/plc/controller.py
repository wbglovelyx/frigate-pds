import threading
import time

import snap7

from frigate.plc.connect import Snap7Client


class PlcController:
    def __init__(self, PlcConfig, LdSingleConfig):
        self.PlcConfig = PlcConfig
        self.LdSingleConfig = LdSingleConfig

    def parse_singel_plc(self, plc, single_plc):
        try:
            if single_plc == 0:
                # 不做处理
                # print("✅ 无需写入信号")
                pass
            elif single_plc == 1:
                # 前进减速
                plc.write_int(snap7.type.Area.MK, 0, 16, 1)
                time.sleep(0.02)
                if plc.read_int(snap7.type.Area.MK, 0, 16) == 1:
                    print("✅ 前进减速信号已成功写入")
                    # single_plc = 0  # 重置信号值
                else:
                    print("❌ 前进减速信号写入失败")
            elif single_plc == 2:
                # 前进停止
                plc.write_int(snap7.type.Area.MK, 0, 17, 1)
                time.sleep(0.02)
                if plc.read_int(snap7.type.Area.MK, 0, 17) == 1:
                    print("✅ 前进停止信号已成功写入")
                    # single_plc = 0  # 重置信号值
                else:
                    print("❌ 前进停止信号写入失败")
            elif single_plc == 3:
                # 后退减速
                plc.write_int(snap7.type.Area.MK, 0, 18, 1)
                time.sleep(0.02)
                if plc.read_int(snap7.type.Area.MK, 0, 18) == 1:
                    print("✅ 后退减速信号已成功写入")
                    # single_plc = 0  # 重置信号值
                else:
                    print("❌ 后退减速信号写入失败")
            elif single_plc == 4:
                # 后退停止
                plc.write_int(snap7.type.Area.MK, 0, 19, 1)
                time.sleep(0.02)
                if plc.read_int(snap7.type.Area.MK, 0, 19) == 1:
                    print("✅ 后退停止信号已成功写入")
                    # single_plc = 0  # 重置信号值
                else:
                    print("❌ 后退停止信号写入失败")
            elif single_plc == 5:
                # 前进停止 + 后退停止
                plc.write_int(snap7.type.Area.MK, 0, 17, 1)
                time.sleep(0.02)
                plc.write_int(snap7.type.Area.MK, 0, 19, 1)
                time.sleep(0.02)
                if (plc.read_int(snap7.type.Area.MK, 0, 17) == 1 and
                        plc.read_int(snap7.type.Area.MK, 0, 19) == 1):
                    print("✅ 前进停止和后退停止信号已成功写入")
                    # single_plc = 0  # 重置信号值
                else:
                    print("❌ 有信号未成功写入")
            else:
                #此时的plc信号错误，重置plc信号的值
                # single_plc = 0
                print("🚫 无效的 PLC 控制信号参数")
        except Exception as e:
            print(f"❌ 控制过程中发生错误: {e}")
            # plc.disconnect()
    def plc_heartbeat_thread(self, plc, stop_event, plc_lock, interval=5):
        print("💓 PLC 心跳线程已启动")
        while not stop_event.is_set():
            try:
                with plc_lock:
                    plc.write_int(snap7.type.Area.MK, 0, 20, 1)
                    print("💓 发送心跳信号 (M20.0=1)")
                time.sleep(5)  # 模拟高低跳变
                with plc_lock:
                    plc.write_int(snap7.type.Area.MK, 0, 20, 0)
                    print("💓 心跳信号归零 (M20.0=0)")
            except Exception as e:
                print(f"❌ 发送心跳信号时发生错误: {e}")
            time.sleep(interval)
        print("🛑 💓 PLC 心跳线程已停止")

    # 这个是通过摄像头数据控制plc的线程，这个线程需要的参数为plc对象，还有队列
    # 从队列中读取int值，读完之后处理，处理完之后接着处理下一个信号值
    def camera_controller_plc_thread(self, plc, camera_plc_queue, plc_lock, stop_event):
        print("📡 摄像头控制 PLC 线程启动")
        while not stop_event.is_set():
            try:
                single_plc = camera_plc_queue.get(timeout=0.1)
                print(f"📡 从摄像头获取 PLC 信号: {single_plc}")
                with plc_lock:
                    self.parse_singel_plc(plc, single_plc)
                    time.sleep(0.1)
            except Exception:
                time.sleep(0.05)  # 无任务则稍作等待
        print("🛑 📡摄像头控制 PLC 线程已停止")

    def ld_controller_plc_thread(self, plc, ld_plc_dict, plc_lock, stop_event):
        if self.LdSingleConfig.enabled:
            print("📥 雷达控制 PLC 线程启动")
            while not stop_event.is_set():
                for radar_name, queue in ld_plc_dict.items():
                    try:
                        # 非阻塞读取（带超时）
                        single_plc = queue.get(timeout=0.05)
                        if radar_name == "head" and single_plc == 1:
                            print(f"📥 从雷达 [{radar_name}] 获取 PLC 信号: {single_plc}")
                            with plc_lock:
                                self.parse_singel_plc(plc, 2)
                                time.sleep(0.1)
                        elif radar_name == "tail" and single_plc == 1:
                            print(f"📥 从雷达 [{radar_name}] 获取 PLC 信号: {single_plc}")
                            with plc_lock:
                                self.parse_singel_plc(plc, 4)
                                time.sleep(0.1)
                        else:
                            pass
                        time.sleep(0.1)
                    except Exception:
                        time.sleep(0.05)  # 当前队列无信号，稍作等待

            print("🛑 📥雷达控制 PLC 线程已停止")



    def run(self, camera_plc_queue, ld_plc_dict, stop_event):
        plc = Snap7Client(self.PlcConfig)
        plc.connect()
        plc_lock = threading.Lock()

        if not plc.connected:
            print("❌ 无法连接到 PLC")
            stop_event.set()
            print("🚫 PLC 控制信号处理已停止")
            return  # ✅ 直接退出

        print("✅ PLC 已连接，启动控制线程")

        # 启动摄像头控制线程
        camera_thread = threading.Thread(
            target=self.camera_controller_plc_thread,
            args=(plc, camera_plc_queue, plc_lock, stop_event),
            name="camera_plc_thread"
        )
        camera_thread.start()

        # 启动雷达控制线程
        ld_thread = threading.Thread(
            target=self.ld_controller_plc_thread,
            args=(plc, ld_plc_dict, plc_lock, stop_event),
            name="ld_plc_thread"
        )
        ld_thread.start()
        # 启动心跳线程
        heartbeat_thread = threading.Thread(
            target=self.plc_heartbeat_thread,
            args=(plc, stop_event, plc_lock),
            name="plc_heartbeat_thread"
        )
        heartbeat_thread.start()
        # 主线程保持运行直到 stop_event 被触发
        try:
            while not stop_event.is_set():
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("🛑 收到中断信号，准备关闭所有线程")
            stop_event.set()
        finally:
            plc.disconnect()
            print("🛠️ 正在等待子线程退出...")
            camera_thread.join()
            ld_thread.join()
            print("✅ 所有 PLC 控制线程已安全退出")


