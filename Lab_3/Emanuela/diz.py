from datetime import datetime
import json
class NEWDEVICE():
      def __init__(self):
        pass
      def insert_new_device(self):
        modifica=input('se il dispositivo è già presente aggiornarlo? y/n: ')
        measureTypeList=[]
        avabservicesList=[]
        ID=int(input('inserire ID:'))
        Name=input('inserire il nome del device:')
        while True:
            measureType=input('inserire le misurazioni, cliccare Q quando si vuole terminare:')
            if measureType=='Q':
                break
            else:
                measureTypeList.append(measureType)
        while True: 
            avabservices=input('inserire i servizi disponibili o cliccare Q per terminare: ')
            if avabservices == 'Q':
                break
            else:
                avabservicesList.append(avabservices)
        servicesDetailsList=[]
        topicList=[]
        serviceditct={}
        for i in range(len(avabservicesList)):
            servT=input('inserire il servizio: ')
            serviceditct["serviceType"]=servT
            serIP=input("inserire l'indirizzo IP: ")
            serviceditct["serviceIP"]=serIP
            for j in range(len(measureTypeList)):
                topic= input('inserire il topic del servizio:')
                topicList.append(topic)
            serviceditct["servicesDetails"]=topicList
            servicesDetailsList.append(serviceditct)
            data=datetime.now()
            data_string = data.strftime("%Y-%m-%d")
            device={
            "deviceID":ID,
            "deviceName":Name,
            "measureType":measureTypeList,
            "availableServices":avabservicesList,
            "servicesDetails":servicesDetailsList,
            "lastUpdate":data_string}
            insertdevice={'modifica':modifica,'device':device}
            
            return (json.dumps(insertdevice))
