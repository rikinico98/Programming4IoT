*********************primo codice**************************************************
                 **Temp_publisher.py**

semplice simulatore di Temperatura
1. SenML formato: self.__message={
                            "bn": sensorID,
                            "e": [{
                                "n": "temperature",
                                "u": "Cel",
                                "t": "",
                                "v":0
                                }]
                        }
2. Alla riga 28 bisogna decidere i range o la distribuzione di temperatura
3. alla riga 38 non ho letto il sensorID, il broker, la porta e il topic dal Catalog 
   per facilitare la simulazione, quindi va modificato

*********************secondo codice**************************************************
                 **Temp_subscriber.py**
semplice subscriber che riceve i dati del publisher e nella funzione "notify" pubblica
i dati sul canale thingspeak tramite una get request

1. righe 15-16-17 ho usato il channelID, l'apikey e l'URL del mio canale thingspeak:
self.channelID = 1321136
self.apikey = 'ZVBAO2QDON8B19X0'
self.baseURL = f"https://api.thingspeak.com/update?api_key={self.apikey}"
vanno poi decisi e aggiunti nel Catalog e presi tramite una get request
2. i valori vengono salvati nel field1 del canale (riga 32)
3. nel main riga 39 anche lì broker, port e topic vanno presi dal Catalog

*********************terzo codice**************************************************
                 **daily_monitor.py**
è il service che prende i dati di temperatura da un apposito canale di thingspeak
ed effettua le media, val max, val min e last update
è possibile ricevere queste informazioni dal Bot telegram "StoreManager" con 
token: 1563644122:AAHM_-LVLMM9RSSSzkCocxwTy4Ms2VI4Z-s

1. righe 55,56,57,58,59 andrebbero prese dal Catalog con delle gte requests
2. la classe Daily_monitor prende i dati dal canale thingspeak e ritorna un messaggio (riga 47):
message = f'STATISTICHE:\nMEDIA: {media}\n
VALORE MASSIMO: {massimo}\n
VALORE MINIMO: {minimo}\n
ULTIMO AGGIORNAMENTO: {last_update}'
N.B.: questo messaggio viene passato al bot telegram

*********************quarto codice**************************************************
                   **Bot.py**
è una prima versione del Bot telegram dove l'unico comando possibile è "/statistiche'
N.B.: nel futuro vanno aggiunti tutti i comandi

*************************************************************************************
MIGLIORIE DA APPORTARE:
1. tutti gli end-points vanno presi e aggiunti nel Catalog.py 
2. Bisogna simulare tanti sensori quante sono le stanze e aggiungere i vari clientID e i topics
3. Dopodichè anche nel Bot telegram bisogna poter selezionare la stanza da cui ricevere le statistiche
