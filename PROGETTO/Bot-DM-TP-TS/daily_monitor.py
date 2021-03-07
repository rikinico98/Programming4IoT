import requests
import json
import time
from datetime import datetime
from Bot import MyBot

class Daily_monitor():
    def __init__(self, baseURL):
        self.baseURL = baseURL        
    def data_retrieve(self):
        r = requests.get(self.baseURL)
        self.diz1 = json.dumps(r.json(), indent = 4)
        #esempio di come si riempie il channel (di self.diz1):
        #{'channel': {'id': 1321136, 'name': 'Temperature', 'description': 'temperature storage', 
        # 'latitude': '0.0', 'longitude': '0.0', 'field1': 'Temperature', 'created_at': '2021-03-07T12:22:57Z',
        #  'updated_at': '2021-03-07T12:22:57Z', 'last_entry_id': 9}, 
        # 'feeds': [{'created_at': '2021-03-07T13:33:09Z', 'entry_id': 1, 'field1': '39'}, 
        # {'created_at': '2021-03-07T13:33:37Z', 'entry_id': 2, 'field1': '5'}, 
        # {'created_at': '2021-03-07T13:35:01Z', 'entry_id': 3, 'field1': '12'}, 
        # {'created_at': '2021-03-07T13:35:50Z', 'entry_id': 4, 'field1': '7'}, 
        # {'created_at': '2021-03-07T13:36:05Z', 'entry_id': 5, 'field1': '37'},
        #  {'created_at': '2021-03-07T13:36:22Z', 'entry_id': 6, 'field1': '-1'},
        #  {'created_at': '2021-03-07T13:36:37Z', 'entry_id': 7, 'field1': '23'},
        #  {'created_at': '2021-03-07T13:36:54Z', 'entry_id': 8, 'field1': '32'},
        #  {'created_at': '2021-03-07T13:37:10Z', 'entry_id': 9, 'field1': '-4'}]}
        self.diz = json.loads(self.diz1)
        print(self.diz)
        misure = self.diz["feeds"]
        #cerco solo le statistiche del giorno corrente
        data = datetime.today().strftime('%Y-%m-%d') #la data corrente
        today_measures = []
        for element in misure:
            if data in element['created_at']: #se la data è quella di oggi
                today_measures.append(element) #riempio la lista solo con le misure di oggi
        
        #prendo solo i valori numerici e li inserisco in valori
        valori = []
        for element in today_measures:
            valori.append(int(element["field1"]))
        
        #calcolo i parametri statistici
        media = sum(valori)/len(valori)
        massimo = max(valori)
        minimo = min(valori)
        last_update = today_measures[-1]['created_at'] #ultimo inserimento
        #creo una stringa con i valori che desidero
        message = f'STATISTICHE:\nMEDIA: {media}\nVALORE MASSIMO: {massimo}\nVALORE MINIMO: {minimo}\nULTIMO AGGIORNAMENTO: {last_update}'
        return message
    

if __name__ == '__main__':
    # vanno fatte le richieste dal Catalog 
    # apikey = requests.get()
    # baseURL = requests.get()
    channelID = 1321136 #va preso dal Catalog
    apikey = 'ZVBAO2QDON8B19X0' #va preso dal Catalog
    channelID = 1321136 #va preso dal Catalog
    baseURL = f'https://api.thingspeak.com/channels/{channelID}/feeds.json?api_key={apikey}' #va preso dal Catalog
    token_bot = '1563644122:AAHM_-LVLMM9RSSSzkCocxwTy4Ms2VI4Z-s' #va preso dal Catalog
    monitor = Daily_monitor(baseURL)
    message = monitor.data_retrieve()
    Bot = MyBot(token_bot, message) #passo al Bot il token e il messaggio che voglio inviare
    #perchè è un thread c'è bisogno di un loop
    while True:
        time.sleep(3)
    
    