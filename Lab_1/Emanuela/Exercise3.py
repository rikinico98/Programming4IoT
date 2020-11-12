#Managing a list of device
from classManageDevices import ManageDevices
import json

if __name__=="__main__":
    obj = ManageDevices("catalog.json")
    print(obj.searchByName("VCNL4010"))
    print(obj.searchByID(3))
    print(obj.searchByService("MQTT"))
    print(obj.searchByMeasureType("Humidity"))
    obj.insertDevice(3)
    print(obj.printAll())
    obj.insertDevice(3)
    print(obj.printAll())
    obj.insertDevice(4)
    print(obj.printAll())
    obj.exit()