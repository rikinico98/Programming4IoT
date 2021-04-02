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
        self.roomID=roomID
    def data_retrieve(self):
        r = requests.get(self.baseURL)
        self.diz1 = json.dumps(r.json(), indent = 4)
        self.diz = json.loads(self.diz1)
 
        d_ID=[]
        d_devName=[]
        field_tot=[]
        dev = requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/devices')
        self.dev_diz1 = json.dumps(dev.json(), indent = 4)
        self.dev_diz = json.loads(self.dev_diz1)
        #print(self.dev_diz)
        for d in self.dev_diz['devices']:
            
            d_ID.append(list(d.keys()))
            d_devName.append(list(d.values()))
            #print(d_ID,d_devName)
        dev=self.dev_diz["devices"]
        #print(dev)
        for n in range(len(d_ID)):
            chiavi=d_ID[n]
            print(chiavi[0])
            field = requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/{chiavi[0]}/get_field')
            self.field_field1 = json.dumps(field.json(), indent = 4)
            self.field_field = json.loads(self.field_field1)
            #print(self.field_field)
            for f in self.field_field["field"]:
                field_tot.append(str(f))
                d_devName.append(dev[n][chiavi[0]])
        
        
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
        
        channel_setting=self.diz['channel']
        channel_ID=channel_setting['id']
        misure = self.diz["feeds"]
        k=list(field_tot)
        k_campi=k
        
        #cerco solo le statistiche del giorno corrente
        yesterday = datetime.now() - timedelta(days=5)
        data=yesterday.strftime('%Y-%m-%d')
        # print(data)
        # data = datetime.today().strftime('%Y-%m-%d') #la data corrente
        today_measures = []
        for element in misure:
            if data in element['created_at']: #se la data è quella di oggi
                today_measures.append(element) #riempio la lista solo con le misure di oggi
        #prendo solo i valori numerici e li inserisco in valori
        valori1 = []
        medie = []
        massimo=[]
        minimo=[]
        last_up=[]
        measure_type=[]
        n_field=[]
        message=''
        for k in k_campi:
            
            valori1 = []
           
            for element in today_measures:
                if element[k] != None:
                   
                    valori1.append(int(float(element[k])))
                    last_update1 = element['created_at'] 
                    last_update1=last_update1.replace('Z', '')
                    last_update1=last_update1.replace('T', ' ')
            if len(valori1) > 0 :
                #print(valori1)
                media1 = sum(valori1)/len(valori1)
                massimo1 = max(valori1)
                minimo1 = min(valori1)
                measure_type.append(channel_setting[k])
                # print(measure_type)
                medie.append(media1)
                massimo.append(massimo1)
                minimo.append(minimo1)
                last_up.append(last_update1)
                n_field.append(k[-1])
            else:
                measure_type.append(channel_setting[k])
                medie.append(None)
                massimo.append(None)
                minimo.append(None)
                last_up.append(None)
                n_field.append(k[-1])
        
        for i in range(len(measure_type)):
            
            if medie[i] != None:
                ThingSpeak_link=f'https://thingspeak.com/channels/{channel_ID}/charts/{n_field[i]}'
                message =message+(f'\nSTATISTICHE: DEVICE-->{str(d_devName[i])}\n{measure_type[i]}\nMEDIA: {medie[i] :.2f}\nVALORE MASSIMO: {massimo[i] :.2f}\nVALORE MINIMO: {minimo[i] :.2f}\nULTIMO AGGIORNAMENTO: {last_up[i]}\nGeneral trend available at:{ThingSpeak_link}')
        
        if len(message)==0:
                message='No measure this day'
        return(message)
  

if __name__ == '__main__':
    pass
