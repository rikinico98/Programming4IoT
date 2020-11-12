import random
import json

from MyMQTT import *
import time
from simplePublisher import *


class BpmSensorJSON(MyPublisher):
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
        self.content=json.load(open('hr_log.json'))
        self.index=0

    def sendData(self):
        message = self.__message
        to_print=self.content[self.index]
        message['e'][0]['v'] = to_print['e'][0]['v']
        message['e'][0]['t'] = to_print['e'][0]['t']
        message['e'][0]['u'] = to_print['e'][0]['u']
        message['e'][0]['n'] = to_print['e'][0]['n']


        self.index=self.index+1



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
    sensor = BpmSensorJSON(s, broker, port)
    sensor.start()
    timeout = time.time() + 60 * 2  # 2 minutes from now
    while True:
        if time.time() > timeout:
            break
        else:
            sensor.sendData()
            time.sleep(5)








