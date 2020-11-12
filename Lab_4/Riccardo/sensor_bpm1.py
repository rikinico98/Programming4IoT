import random
import json
import numpy as np
from MyMQTT import *
import time
from simplePublisher import *


class BpmSensor(MyPublisher):
    """docstring for Sensor"""

    def __init__(self, sensorID, broker, port):

        self.sensorID = str(sensorID)
        self.topic = '/'.join([ self.sensorID])
        self.client = MyMQTT(self.sensorID, broker, port, None)
        self.__message = {

            'bn': self.sensorID,
            'e':
                [
                    {'n': 'heartrate', 'u': 'Bpm', 't': '', 'v': ''}
                ]
        }

    def sendData(self):
        message = self.__message
        shape, scale = 1, 0.5  # mean=4, std=2*sqrt(2)
        a = 40 * np.random.gamma(shape, scale, 1000) + 55
        message['e'][0]['v'] = a[0]
        message['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, message)

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()


if __name__ == '__main__':
    conf = json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    s = 'IoT_project/Riccardo_bpm'
    sensor = BpmSensor(s, broker, port)
    sensor.start()
    timeout = time.time() + 60 * 2  # 2 minutes from now
    while True:
        if time.time() > timeout:
            break
        else:
            sensor.sendData()
            time.sleep(5)








