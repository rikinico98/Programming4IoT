import requests
import json


if __name__ == "__main__":
    to_add = {
        "deviceID": 18,
        "deviceName": "chico",
        "measureType": ["Temperature", "Humidity"],
        "availableServices": ["MQTT", "REST"],
        "servicesDetails": [
            {
                "serviceType": "MQTT",
                "serviceIP": "mqtt.eclipse.org",
                "topic": ["MySmartThingy/1/temp", "MySmartThingy/1/hum"]
            },
            {
                "serviceType": "ciao",
                "serviceIP": "dht11.org:8080"
            }
        ],
        "lastUpdate": "2020-03-30"
    }





    while True:

        print('---MENU---\n1)Search by name\n2)Search by ID\n3)Search by measure type\n4)Print all\n5)Insert device\n6)Save and close')

        cmd1 = input('Select command\n')

        if cmd1 == '1':
            cmd2 = input('Enter input\n')
            URL = (f'http://127.0.0.1:8080/search_name/{cmd2}')
            r = requests.get(URL)
            if (r.status_code == 200):
                body = json.dumps(r.json(), indent=4)
                content_dict = json.loads(body)
                for device in content_dict:
                    for key in device.keys():
                        print(key, ' : ', device[key])
            else:
                if r.status_code == 405:
                    print("ERROR:DEVICE ABSENT")
                else:
                    print("CRITICAL ERROR")



        elif cmd1=='2':
            cmd2 = input('Enter input\n')
            URL = (f'http://127.0.0.1:8080/search_ID/{cmd2}')
            r = requests.get(URL)
            if (r.status_code == 200):
                body = json.dumps(r.json(), indent=4)
                content_dict = json.loads(body)
                for device in content_dict:
                    for key in device.keys():
                        print(key, ' : ', device[key])
            else:
                if r.status_code == 405:
                    print("ERROR:DEVICE ABSENT")
                else:
                    print("CRITICAL ERROR")



        elif cmd1=='3':
            cmd2 = input('Enter input\n')
            URL = (f'http://127.0.0.1:8080/search_meas_type/{cmd2}')
            r = requests.get(URL)
            if (r.status_code == 200):
                body = json.dumps(r.json(), indent=4)
                content_dict = json.loads(body)
                for device in content_dict:
                    for key in device.keys():
                        print(key, ' : ', device[key])
            else:
                if r.status_code == 405:
                    print("ERROR:DEVICE ABSENT")
                else:
                    print("CRITICAL ERROR")


        elif cmd1=='4':
            URL = (f'http://127.0.0.1:8080/print_all')
            r = requests.get(URL)
            body = json.dumps(r.json(), indent=4)
            td = json.loads(body)
            for key, value in td.items():
                if key == 'devicesList':
                    devices=td['devicesList']
                    print('devicesList : \n')
                    i=1
                    for device in devices:
                        print('DEVICE',i,':\n')
                        i=i+1
                        for key_s, value_s in device.items():
                            print(key_s, ' : ', value_s)


                else:
                    print(key, ' : ', value)
        elif cmd1=='5':
            URL = (f'http://127.0.0.1:8080')
            r=requests.put(URL,data=json.dumps(to_add))
            a=2
        elif cmd1=='6':
            URL = (f'http://127.0.0.1:8080/print_all')
            r = requests.get(URL)
            body = json.dumps(r.json(), indent=4)
            content_dict = json.loads(body)
            json.dump(content_dict, open('catalog.json', 'w', ), indent=4)
            exit(0)





