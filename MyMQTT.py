import paho.mqtt.client as PahoMQTT
import json
class MyMQTT:

    def __init__(self, clientID, broker, port, notifier):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.clientID = clientID
        self._topic = []
        self._isSubscriber = False
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID,True)  
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessage
        self._paho_mqtt.on_publish = self.myOnPublish
 
 
    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print(f"Connected to {self.broker} with result code {rc}")

    def myOnMessage(self, paho_mqtt , userdata, msg):
        # A new message is received
        self.notifier.notify (msg.topic, msg.payload, msg.qos)

    def myOnPublish (self, paho_mqtt, userdata, mid):
    	print(f"Message published: {mid}\nFrom device {paho_mqtt}")
 
    def myPublish (self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)

    def mySubscribe (self, topic):
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2) 
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic.append(topic)
        print ("subscribed to %s" % (topic))
 
    def start(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()
            
    def stop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            for topic in self._topic:
                self._paho_mqtt.unsubscribe(topic)
 
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()