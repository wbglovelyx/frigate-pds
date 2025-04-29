import json
import time

import paho.mqtt.client as mqtt


class MQTTSubscriber:
    def __init__(self, ip, port, username, password, topic, queue, flag_plc): #, red_queue, ld2410b_queue, ld6002b_queue
        self.client_id = "python_subscriber_1"
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic
        self.queue = queue
        self.flag_plc = flag_plc #bool true时代表控制plc，false时代表页面展示
        self.keepalive = 60
        self.qos = 1
        self.clean_session = False
        self._create_client()


    def _create_client(self):
        """
        创建 MQTT 客户端并设置回调函数。
        - 配置连接、消息接收、断开连接的回调。
        """
        self.client = mqtt.Client(
            callback_api_version = mqtt.CallbackAPIVersion.VERSION1,
            client_id=self.client_id,
            clean_session=self.clean_session,
            protocol=mqtt.MQTTv311
        )

        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        # 设置认证信息
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

    def _on_connect(self, client, userdata, flags, rc):
        """
        连接成功时的回调函数。
        - 如果连接成功，订阅主题。
        """
        # print(f"Connected with result code: {rc}")
        if rc == 0:
            # print("Successfully connected to MQTT broker!")
            client.subscribe(self.topic, qos=self.qos)
        else:
            print(f"Connection failed with code {rc}")
            time.sleep(5)
            client.reconnect()

    def _on_message(self, client, userdata, msg):
        """
        消息接收时的回调函数，接收到消息后打印并将其添加到队列。
        """
        try:
            payload = msg.payload.decode('utf-8')
            if self.flag_plc:
                # 用于界面展示的消息
                message_show = {
                    "topic": msg.topic,
                    "payload": payload,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.queue.put(message_show)
            else:
                # 控制plc的消息
                message_plc = {
                    "payload": payload,
                }
                self.queue.put(message_plc)
        except UnicodeDecodeError:
            print(f"Received binary message: {msg.payload}")
            message = {
                "topic": msg.topic,
                "payload": str(msg.payload),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.message = json.dumps(message)
            print(f"Received binary message: {self.message}")
            self.message_queue.put(message)

    def _on_disconnect(self, client, userdata, rc, *args):
        """
        连接断开时的回调函数。
        - 如果连接断开非正常状态，自动重新连接。
        """
        if rc != 0:
            print(f"Unexpected disconnection. Auto-reconnecting... (Code: {rc})")
            client.reconnect()

    def start(self):
        """
        启动 MQTT 客户端并开始监听消息。
        """
        try:
            self.client.connect_async(
                host=self.ip,
                port=self.port,
                keepalive=self.keepalive
            )
            self.client.loop_start()

            # 保持主线程运行
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nDisconnecting gracefully...")
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            print(f"Critical error: {str(e)}")
            exit(1)

# if __name__ == "__main__":
#     # 示例代码
#     red_queue = queue.Queue(maxsize=5)

#     MQTTSubscriber_red = MQTTSubscriber("192.168.0.45", 1883, "first", "123", "djc_dong/ld/2410b", red_queue, False)
#     MQTTSubscriber_red.start()

