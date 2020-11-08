import SensorManager as mysensor

if __name__=="__main__":

    catalog= mysensor.SensorManager('UsefulFiles\catalog.json')
    # catalog.searchByName('DHT11')
    # catalog.searchByID(1)
    # catalog.searchByMeasureType('Temperature')
    to_add={
            "deviceID":4,
            "deviceName":"hola",
            "measureType":["Temperature","Humidity"],
            "availableServices":["MQTT","REST"],
            "servicesDetails":[
                    {
                    "serviceType":"MQTT",
                    "serviceIP":"mqtt.eclipse.org",
                    "topic":["MySmartThingy/1/temp","MySmartThingy/1/hum"]
                    },
                    {
                        "serviceType":"ciao",
                        "serviceIP":"dht11.org:8080"
                    }
                ],
            "lastUpdate":"2020-03-30"
        }
    catalog.insertDevice(to_add)
    catalog.printAll()
    catalog.save_all()



