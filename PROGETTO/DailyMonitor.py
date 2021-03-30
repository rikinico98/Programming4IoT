import requests
import json
from datetime import datetime, timedelta


# INSERIRE IL TIMEDELTA CORRETTO, ADESSO è A 2 GIORNI PERCHè AVEVO I DATI VECCHI
class Daily_monitor():
    def __init__(self, roomID):
        r_TS = requests.get(f'http://127.0.0.1:8070/catalog/{roomID}/TS_utilities')
        j_TS = json.dumps(r_TS.json(), indent=4)
        d_TS = json.loads(j_TS)
        TS = d_TS["ThingSpeak"]
        self.apikey = TS["api_key_read"]
        self.channelID = TS["channelID"]
        self.baseURL = f'https://api.thingspeak.com/channels/{self.channelID}/feeds.json?api_key={self.apikey}'

    def data_retrieve(self):
        r = requests.get(self.baseURL)
        self.diz1 = json.dumps(r.json(), indent=4)
        self.diz = json.loads(self.diz1)
        # print(self.diz)
        # esempio di come si riempie il channel (di self.diz1):
        # {'channel':{'id': 1321136, 'name': 'Temperature', 'description': 'temperature storage',
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

        channel_setting = self.diz['channel']
        misure = self.diz["feeds"]
        k = list(misure[0].keys())
        k_campi = k[2:len(k)]
        # cerco solo le statistiche del giorno corrente

        yesterday = datetime.now() - timedelta(days=2)
        data = yesterday.strftime('%Y-%m-%d')
        # data = datetime.today().strftime('%Y-%m-%d') #la data corrente
        today_measures = []
        for element in misure:
            if data in element['created_at']:  # se la data è quella di oggi
                today_measures.append(element)  # riempio la lista solo con le misure di oggi
        # prendo solo i valori numerici e li inserisco in valori
        valori1 = []
        medie = []
        massimo = []
        minimo = []
        last_up = []
        measure_type = []
        message = ''
        for k in k_campi:
            valori1 = []

            for element in today_measures:

                if element[k] != None:
                    valori1.append(int(float(element[k])))
                    last_update1 = element['created_at']
                    last_update1 = last_update1.replace('Z', '')
                    last_update1 = last_update1.replace('T', ' ')
            media1 = sum(valori1) / len(valori1)
            massimo1 = max(valori1)
            minimo1 = min(valori1)
            measure_type.append(channel_setting[k])
            medie.append(media1)
            massimo.append(massimo1)
            minimo.append(minimo1)
            last_up.append(last_update1)
        for i in range(len(measure_type)):
            message = message + (
                f'\nSTATISTICHE:\n{measure_type[i]}\nMEDIA: {medie[i] :.2f}\nVALORE MASSIMO: {massimo[i] :.2f}\nVALORE MINIMO: {minimo[i] :.2f}\nULTIMO AGGIORNAMENTO: {last_up[i]}')
        return message


if __name__ == '__main__':
    pass
