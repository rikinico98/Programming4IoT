import random
import json
from MyMQTT import *
import time


class DataCollector():
    """docstring for Sensor"""

    def __init__(self, clientID, broker, baseTopic):
        self.clientID = clientID
        self.baseTopic = baseTopic
        self.client = MyMQTT(clientID, broker, 1883, self)
        self.total_content=[]

    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))

    def end(self):
        json.dump(self.total_content, open('temp_log.json', 'w', ), indent=4)
        self.client.stop()
        print('{} has stopped'.format(self.clientID))

    def follow(self, topic):
        self.client.mySubscribe(topic)

    def notify(self, topic, msg):
        payload = json.loads(msg)
        self.total_content.append(payload)
        print(json.dumps(payload, indent=4))


if __name__ == '__main__':
    conf = json.load(open("settings.json"))
    coll = DataCollector('Ricky' + str(random.randint(1, 10 ** 5)), conf["broker"], baseTopic=conf["baseTopic"])
    coll.run()
    print(f'This is the client to follow the data coming from the sensors of the building of {coll.baseTopic}')
    choice = ''
    while choice != 'q':
        print("What kind of data you want to retrieve")
        print("\ts: data from the sensor")
        print("\tc: to go back to this menu")
        print("\tq: to quit")
        choice = input()
        if choice == 'q':
            break
        while choice != 'c':
            if choice == 's':
                coll.client.unsubscribe()
                coll.follow(coll.baseTopic + '/Riccardo_temperature')

            choice = input()
        coll.client.unsubscribe()

    coll.client.unsubscribe()
    coll.end()



