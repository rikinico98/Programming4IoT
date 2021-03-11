il sensore temp hum invia contemporaneamente le misure di temperatura e umidità
costruito a partire da quello caricato da Caterina ho aggiunto la simulazione di umidità
e sul subscriber ho fatto in modo che invii i dati allo stesso canale thingspeak che ha 2 campi
uno per la temperatura "Field1" e uno per l'umidità "Field2"
La pubblicazione è sfasata di 15 secondi perchè altrimenti si sovrappone la comunicazione 
e non prende la seconda delle misurazioni.