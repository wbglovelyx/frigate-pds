import multiprocessing as mp
import queue
import signal
import threading
import time

from setproctitle import setproctitle

from frigate.ld_score.mqtt_ld import MQTTSubscriber


class LdScoreManages():
    def __init__(self, name, config, score_dist):
        self.name = name
        self.config = config
        self.score_dist = score_dist
        self.red_score = 0.00
        self.ld2410b_score = 0.00
        self.ld6002b_score = 0.00
        self.red_length = config.topics.red_queue_length
        self.ld2410b = config.topics.ld2410b_queue_length
        self.ld6002b = config.topics.ld6002b_queue_length
        self.red_queue = queue.Queue(maxsize=self.red_length)
        self.ld2410b_queue = queue.Queue(maxsize=config.topics.ld2410b_queue_length)
        self.ld6002b_queue = queue.Queue(maxsize=config.topics.ld6002b_queue_length)
        self.MQTTSubscriber_red = MQTTSubscriber(config.ip, config.port, config.username, config.password, config.topics.red, self.red_queue, False)
        self.MQTTSubscriber_ld2410b = MQTTSubscriber(config.ip, config.port, config.username, config.password, config.topics.ld2410b, self.ld2410b_queue, False)
        self.MQTTSubscriber_ld6002b = MQTTSubscriber(config.ip, config.port, config.username, config.password, config.topics.ld6002b, self.ld6002b_queue, False)

    def thread_read_red_data(self):
        """
        启动Red传感器的MQTT订阅线程
        """
        red_thread = threading.Thread(target=self.MQTTSubscriber_red.start)
        red_thread.daemon = True  # 守护线程，在主线程退出时自动退出
        red_thread.start()
        # 从队列中获取数据，然后判断，更新分数
        while True:
            red_have_people = 0
            for i in range(self.red_length):
                red_have_people = red_have_people + 1
            self.red_score = red_have_people / self.red_length
            time.sleep(0.01)

    def thread_read_2410b_data(self):
        """
        启动LD2410B传感器的MQTT订阅线程
        """
        ld2410b_thread = threading.Thread(target=self.MQTTSubscriber_ld2410b.start)
        ld2410b_thread.daemon = True
        ld2410b_thread.start()
        while True:
            ld2410b_have_people = 0
            for i in range(self.red_length):
                ld2410b_have_people = ld2410b_have_people + 1
            self.ld2410b_score = ld2410b_have_people / self.ld2410b_score
            time.sleep(0.01)

    def thread_read_6002b_data(self):
        """
        启动LD6002B传感器的MQTT订阅线程
        """
        ld6002b_thread = threading.Thread(target=self.MQTTSubscriber_ld6002b.start)
        ld6002b_thread.daemon = True
        ld6002b_thread.start()
        while True:
            ld6002_have_people = 0
            for i in range(self.red_length):
                ld6002_have_people = ld6002_have_people + 1
            self.ld6002b_score = ld6002_have_people / self.ld6002b_score
            time.sleep(0.01)

    def ld_data_score(self):
        """
        数据评分或处理逻辑
        """
        while True:
            score = self.ld2410b_score + self.ld6002b_score + self.red_score
            self.score_dist.self.name = score


    def run(self):
        """
        启动所有线程，并开始运行数据读取与处理。
        """
        # 启动各个传感器数据的MQTT订阅线程
        self.thread_read_red_data()
        self.thread_read_2410b_data()
        self.thread_read_6002b_data()

        # 在主线程中运行数据评分
        self.ld_data_score()


def ld_data_process(name, config, score_dist):
    # 处理雷达数据的逻辑
    stop_event = mp.Event()

    def receiveSignal(signalNumber, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)

    threading.current_thread().name = f"capture:{name}"
    setproctitle(f"frigate.capture:{name}")

    while not stop_event.is_set():
        ld_score = LdScoreManages(name, config, score_dist)
        ld_score.run()


