import queue
import signal
import threading
import time

from frigate.ld_score.mqtt_ld import MQTTSubscriber


class LdScoreManages():
    def __init__(self, name, config, red_score_dict, ld2410b_score_dict, ld6002b_score_dict, stop_event):
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
        time.sleep(1)
        while not self.stop_event.is_set():
            with self.lock_red_score:
                self.red_score_dict[self.name] = self.red_score
            with self.lock_2410b_score:
                self.ld2410b_score_dict[self.name] = self.ld2410b_score
            with self.lock_6002b_score:
                self.ld6002b_score_dict[self.name] = self.ld6002b_score
            time.sleep(0.05)


def ld_data_process(name, config, red_score_queue, ld2410b_score_queue, ld6002b_score_queue, stop_event):
    # 处理雷达数据的逻辑

    def receiveSignal(signalNumber, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)
    ld_score = LdScoreManages(name, config, red_score_queue, ld2410b_score_queue, ld6002b_score_queue, stop_event)
    while not stop_event.is_set():
        ld_score.run()


