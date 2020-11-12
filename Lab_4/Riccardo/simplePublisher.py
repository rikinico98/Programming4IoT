import paho.mqtt.client as PahoMQTT

class MyPublisher:
    def __init__(self,clientID,broker):
        self.clientID=clientID
        #create an instance of paho.mqtt.client
        self._paho_mqtt=PahoMQTT.Client(self.clientID,True)
        #register the callback
        self._paho_mqtt.on_connect=self.myOnConnect
        self.messageBroker= broker
    def star(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.messageBroker,1883)
        self._paho_mqtt.loop_start()
    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
    def myInCOnnect(self,paho_mqtt,userdata,flags,rc):
        print('Connected to %s with result code : %d'(self.messageBroker,rc))

    def myPublish(self,topic,message):
        #publish a message with a certain topic
        self._paho_mqtt.publish(topic,message,2)

