Per aggiungere un prodotto al database:
inviare una richiesta PUT a Database_StoredProducts.py con il seguente formato:
db/ID_stanza/ID_prodotto/new
body atteso:
{"product_ID" : ID_prodotto (string: ex. "000"), "quantity": numero intero (int: ex. 50), "product_type": codice_prodotto (string: ex. "00")}

Possibili errori:
401, "Unexpected command - Wrong Command"
506, "Room not found"
400, "Product type different from the room one"

#############################################################################################################################################
Per vendere un prodotto (rimuoverlo dal magazzino ed aggiungerlo al database dei prodotti venduti)
inviare una richiesta DELETE a Database_StoredProducts.py con il seguente formato:
db/ID_stanza/ID_prodotto/delete
body atteso:
{"product_ID" : ID_prodotto (string: ex. "000"), "quantity": numero intero (int: ex. 50), "product_type": codice_prodotto (string: ex. "00")}
Dove quantity in questo caso è la quantità di prodotto da vendere.
NOTA!!!! : il body passato al DELETE deve essere una sola riga!!!!

Possibili errori:
401, "Unexpected command - Wrong Command"
506, "Room not found"
400, "Product type different from the room one"
413, "There are not enough products to sell"

#############################################################################################################################################
Per ottenere le statistiche sui prodotti in magazzino e su quelli venduti:
inviare una richiesta GET a Statistics_products.py con i seguenti formati:
db/all                                            # retrieve all sold and stored products
db/sold/all                                       # retrieve all sold products
db/stored/all                                     # retrieve all stored products
db/stored/ID_stanza/all                           # retrieve all the products stored in ID_stanza
db/stored/ID_stanza/ID_prodotto/all               # retrieve the product ID_prodotto from the room ID_stanza
db/stored/threshold/all?th=num                    # retrieve all products whose quantity is smaller than num
db/stored/ID_stanza/threshold/all?th=num          # retrieve all products whose quantity is smaller than num in ID_stanza
db/sold/most/all                                  # retrieve the best-selling product
db/sold/least/all                                 # recover the least sold product
db/sold/ID_stanza/most/all                        # retrieve the best-selling product in room ID_stanza
db/sold/ID_stanza/least/all                       # recover the least sold product in ID_stanza
db/sold/most/month/all?month=num_month            # retrieve the best-selling product in month "month"
db/sold/least/month/all?month=num_month           # recover the least sold product in month "month"
db/sold/ID_stanza/most/month/all?month=num_month  # retrieve the best-selling product in month "month" in ID_stanza
db/sold/ID_stanza/least/month/all?month=num_month # recover the least sold product in month "month" in ID_stanza
db/sold/most/year/all?year=num_year               # retrieve the best-selling product in year "year"
db/sold/least/year/all?year=num_year              # recover the least sold product in year "year"
db/sold/ID_stanza/most/year/all?year=num_year     # retrieve the best-selling product in year "year" in ID_stanza
db/sold/ID_stanza/least/year/all?year=num_year    # recover the least sold product in year "year" in ID_stanza
db/statistics/count/all                           # return the total number of products in the warehouse
db/statistics/count/ID_stanza/all                 # return the total number of products in ID_stanza
db/statistics/mean/all                            # return the mean value of the products sold
db/statistics/total/all                           # return the total value of the products sold
db/statistics/mode/all                            # return the products that are more present in the warehouse
db/statistics/mode/ID_stanza/all                  # return the products that are more present in ID_stanza

Possibili errori:
401, "Unexpected command - Wrong Command"
