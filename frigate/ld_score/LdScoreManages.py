import queue
import signal
import threading
import time

from frigate.ld_score.mqtt_ld import MQTTSubscriber


class LdScoreManages():
    def __init__(self, name, config, red_score_dict, ld2410b_score_dict, ld6002b_score_dict, single_ld_config, ld_plc_dict, stop_event):
        self.name = name
        self.config = config
        self.red_score = 0.0
        self.ld2410b_score = 0.0
        self.ld6002b_score = 0.0
        self.red_length = config.topics.red_queue_length
        self.ld2410b_length = config.topics.ld2410b_queue_length
        self.ld6002b_length = config.topics.ld6002b_queue_length
        self.red_queue = queue.Queue(maxsize=self.red_length)
        self.ld2410b_queue = queue.Queue(maxsize=self.ld2410b_length)
        self.ld6002b_queue = queue.Queue(maxsize=self.ld6002b_length)
        '''此处开始处理单独使用雷达的配置，把配置文件的信息进行读取'''
        self.ld_plc_dict = ld_plc_dict
        self.single_ld_config = single_ld_config
        self.enalbe = self.single_ld_config.enabled
        self.weight_2410b = self.single_ld_config.weight_2410b
        self.weight_6002b = self.single_ld_config.weight_6002b
        self.weight_red = self.single_ld_config.weight_red
        self.stop = self.single_ld_config.stop#用于判断是否停车的阈值
        #在此处传入了plc信号的队列，下面就开始往队列里面填写数据，填写数据的操作在计算总分数的线程中进行
        '''此处结束读取单独使用雷达的配置'''
        self.MQTTSubscriber_red = MQTTSubscriber(config.ip, config.port, config.username, config.password, config.topics.red, self.red_queue, "ld_data_red", False)
        self.MQTTSubscriber_ld2410b = MQTTSubscriber(config.ip, config.port, config.username, config.password, config.topics.ld2410b, self.ld2410b_queue, "ld_data_2410b", False)
        self.MQTTSubscriber_ld6002b = MQTTSubscriber(config.ip, config.port, config.username, config.password, config.topics.ld6002b, self.ld6002b_queue, "ld_data_6002b", False)
        # 创建锁用来控制分数的计算
        self.lock_red_score = threading.Lock()
        self.lock_2410b_score = threading.Lock()
        self.lock_6002b_score = threading.Lock()
        self.red_score_dict = red_score_dict
        self.ld2410b_score_dict = ld2410b_score_dict
        self.ld6002b_score_dict = ld6002b_score_dict
        self.stop_event = stop_event

    def thread_read_red_data(self, lock):
        """
        启动Red传感器的MQTT订阅线程
        """
        red_thread_mqtt = threading.Thread(target=self.MQTTSubscriber_red.start)
        red_thread_mqtt.daemon = True  # 守护线程，在主线程退出时自动退出
        red_thread_mqtt.start()
        # 从队列中获取数据，然后判断，更新分数
        while not self.stop_event.is_set():
            red_have_people = 0
            for i in range(self.red_length):
                try:
                    if self.red_queue.get(0.05) == "1":
                        red_have_people = red_have_people + 1

                except queue.Empty:
                    continue
            with lock:
                self.red_score = red_have_people / self.red_length
            time.sleep(0.01)

    def thread_read_2410b_data(self, lock):
        """
        启动LD2410B传感器的MQTT订阅线程
        """
        ld2410b_thread_mqtt = threading.Thread(target=self.MQTTSubscriber_ld2410b.start)
        ld2410b_thread_mqtt.daemon = True
        ld2410b_thread_mqtt.start()
        while not self.stop_event.is_set():
            ld2410b_have_people = 0
            for i in range(self.ld2410b_length):
                if self.ld2410b_queue.get() == "1":
                    ld2410b_have_people = ld2410b_have_people + 1
            with lock:
                self.ld2410b_score = ld2410b_have_people / self.ld2410b_length
            time.sleep(0.05)

    def thread_read_6002b_data(self, lock):
        """
        启动LD6002B传感器的MQTT订阅线程
        """
        ld6002b_thread_mqtt = threading.Thread(target=self.MQTTSubscriber_ld6002b.start)
        ld6002b_thread_mqtt.daemon = True
        ld6002b_thread_mqtt.start()
        while not self.stop_event.is_set():
            ld6002_have_people = 0
            for i in range(self.ld6002b_length):
                try:
                    if self.ld6002b_queue.get(0.05) == "1":
                        ld6002_have_people = ld6002_have_people + 1
                except queue.Empty:
                    continue
            with lock:
                self.ld6002b_score = ld6002_have_people / self.ld6002b_length
            time.sleep(0.05)

    def thread_calculate_score(self, name, lock_red, lock_2410b, lock_6002b, ld_plc_dict):
        """
        计算综合分数的线程
        """
        last_signal = None  # 上一次发送的信号，避免重复发送

        while True:
            with lock_red:
                red_score = self.red_score
            with lock_2410b:
                ld2410b_score = self.ld2410b_score
            with lock_6002b:
                ld6002b_score = self.ld6002b_score

            total_score = (red_score * self.weight_red) + \
                        (ld2410b_score * self.weight_2410b) + \
                        (ld6002b_score * self.weight_6002b)

            signal = 1 if total_score >= self.stop else 0
            action = "是" if signal else "否"

            if signal != last_signal:
                try:
                    if ld_plc_dict[name].full():
                        ld_plc_dict[name].get_nowait()
                    ld_plc_dict[name].put_nowait(signal)
                    last_signal = signal
                except queue.Full:
                    print(f"⚠️ 队列 {name} 已满，无法放入信号")
                except queue.Empty:
                    print(f"⚠️ 队列 {name} 为空，无法取出信号")

            # # 输出调试信息
            # print("---------------------------------此处为雷达单独的探测结果----------------------------------")
            # print(f"LD Name: {name}")
            # print(f"Red Score: {red_score:.2f}, LD2410B Score: {ld2410b_score:.2f}, LD6002B Score: {ld6002b_score:.2f}, Total Score: {total_score:.2f}")
            # print(f"是否停车: {action}")
            # print("---------------------------------------------------------------------------------------")

            time.sleep(0.1)
    def run(self):
        # 开启线程计算分数，计算分数后写入队列
        ld_thread_red = threading.Thread(target=self.thread_read_red_data, args=(self.lock_red_score,))
        ld_thread_red.daemon = True
        ld_thread_red.start()

        ld_thread_ld2410b = threading.Thread(target=self.thread_read_2410b_data, args=(self.lock_2410b_score,))
        ld_thread_ld2410b.daemon = True
        ld_thread_ld2410b.start()

        ld_thread_ld6002b = threading.Thread(target=self.thread_read_6002b_data, args=(self.lock_6002b_score,))
        ld_thread_ld6002b.daemon = True
        ld_thread_ld6002b.start()

        if self.enalbe:
            ld_thread_calculate = threading.Thread(target=self.thread_calculate_score, args=(self.name,self.lock_red_score, self.lock_2410b_score, self.lock_6002b_score, self.ld_plc_dict))
            ld_thread_calculate.daemon = True
            ld_thread_calculate.start()

        time.sleep(1)
        while not self.stop_event.is_set():
            with self.lock_red_score:
                self.red_score_dict[self.name] = self.red_score
                # print(f"Red Score for {self.name}: {self.red_score:.2f}")
            with self.lock_2410b_score:
                self.ld2410b_score_dict[self.name] = self.ld2410b_score
                # print(f"LD2410B Score for {self.name}: {self.ld2410b_score:.2f}")
            with self.lock_6002b_score:
                self.ld6002b_score_dict[self.name] = self.ld6002b_score
                # print(f"LD6002B Score for {self.name}: {self.ld6002b_score:.2f}")
            time.sleep(0.05)


def ld_data_process(name, config, red_score_queue, ld2410b_score_queue, ld6002b_score_queue, single_ld_config, ld_plc_dict, stop_event):
    # 处理雷达数据的逻辑

    def receiveSignal(signalNumber, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)
    ld_score = LdScoreManages(name, config, red_score_queue, ld2410b_score_queue, ld6002b_score_queue, single_ld_config, ld_plc_dict, stop_event)
    while not stop_event.is_set():
        ld_score.run()


