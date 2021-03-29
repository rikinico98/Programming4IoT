import requests
import json
from datetime import datetime

class Daily_monitor():
    def __init__(self,roomID):

        r = requests.get(f'http://127.0.0.1:8070/catalog/{roomID}/TS_utilities')
        body = json.dumps(r.json(), indent=4)
        retrivedDict = json.loads(body)
        ThingSpeak = retrivedDict['ThingSpeak']
        self.channelID = ThingSpeak['channelID']
        self.apikey = ThingSpeak['api_key_read']
        self.baseURL = f'https://api.thingspeak.com/channels/{self.channelID}/feeds.json?api_key={self.apikey}'
    def data_retrieve(self):
        r = requests.get(self.baseURL)
        body = json.dumps(r.json(), indent=4)
        self.diz1 = json.loads(body)
        # print(self.diz1)
        #esempio di come si riempie il channel (di self.diz1):
        #{'channel':{'id': 1321136, 'name': 'Temperature', 'description': 'temperature storage', 
        # 'latitude': '0.0', 'longitude': '0.0', 'field1': 'Temperature', 'created_at': '2021-03-07T12:22:57Z',
        # 'updated_at': '2021-03-07T12:22:57Z', 'last_entry_id': 9}, 
        # 'feeds': [{'created_at': '2021-03-07T13:33:09Z', 'entry_id': 1, 'field1': '39'}, 
        # {'created_at': '2021-03-07T13:33:37Z', 'entry_id': 2, 'field1': '5'}, 
        # {'created_at': '2021-03-07T13:35:01Z', 'entry_id': 3, 'field1': '12'}, 
        # {'created_at': '2021-03-07T13:35:50Z', 'entry_id': 4, 'field1': '7'}, 
        # {'created_at': '2021-03-07T13:36:05Z', 'entry_id': 5, 'field1': '37'},
        # {'created_at': '2021-03-07T13:36:22Z', 'entry_id': 6, 'field1': '-1'},
        # {'created_at': '2021-03-07T13:36:37Z', 'entry_id': 7, 'field1': '23'},
        # {'created_at': '2021-03-07T13:36:54Z', 'entry_id': 8, 'field1': '32'},
        # {'created_at': '2021-03-07T13:37:10Z', 'entry_id': 9, 'field1': '-4'}]}
        self.diz = json.loads(self.diz1)
        
        misure = self.diz["feeds"]
        #cerco solo le statistiche del giorno corrente
        data = datetime.today().strftime('%Y-%m-%d') #la data corrente
        today_measures = []
        for element in misure:
            if data in element['created_at']: #se la data è quella di oggi
                today_measures.append(element) #riempio la lista solo con le misure di oggi
        
        #prendo solo i valori numerici e li inserisco in valori
        valori1 = []
        valori2 = []

        for element in today_measures:
            
            if element["field1"] != None:
             valori1.append(int(element["field1"]))
             last_update1 = element['created_at'] 
             last_update1=last_update1.replace('Z', '')
             last_update1=last_update1.replace('T', ' ')
            if element["field2"] != None:
             valori2.append(int(element["field2"]))
             last_update2 = element['created_at'] 
             last_update2=(last_update2.replace('Z', ''))
             last_update2=(last_update2.replace('T', ' '))
        #calcolo i parametri statistici
        media1 = sum(valori1)/len(valori1)
        massimo1 = max(valori1)
        minimo1 = min(valori1)
        media2 = sum(valori2)/len(valori2)
        massimo2 = max(valori2)
        minimo2 = min(valori2)
        # last_update = today_measures[-1]['created_at'] #ultimo inserimento
        #creo una stringa con i valori che desidero
        message = f'STATISTICHE:\nTEMPERATURA\nMEDIA: {media1}\nVALORE MASSIMO: {massimo1}\nVALORE MINIMO: {minimo1}\nULTIMO AGGIORNAMENTO: {last_update1}\nHUMIDITY\nMEDIA:{media2}\nVALORE MASSIMO: {massimo2}\nVALORE MINIMO: {minimo2}\nULTIMO AGGIORNAMENTO: {last_update2}'
        return message
    

if __name__ == '__main__':
    pass

 
    
    
