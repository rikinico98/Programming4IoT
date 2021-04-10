import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import BarcodeScanner
from MyMQTT import *
import requests
import DailyMonitor

class WareBot:


    def __init__(self,token,topic,broker,port,APIs):
        #############--IP per le richieste--#################
        self.catalog_IP=APIs['catalogIP']
        self.database_stats_URL = APIs['databaseStatsIP']
        self.stored_products_IP = APIs['storedProductsIP']
        #Definisco il nome del client, topic, e MyMqtt object per la registrazione MQTT
        self.clientID = APIs['clientID_MQTT']
        self.topic = topic
        self.client = MyMQTT(self.clientID, broker, port, self)
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        # Definisco il bot con il token
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot,
                    {'chat': self.on_chat_message,
                     'callback_query': self.on_callback_query}).run_as_thread()
        # Tenere traccia di ogni comunicazione tramite Telegram con una lista di dict che contiene:
        # {
        #     'isRegister':True/False,
        #     'Log_in_status':0 ----> Se l'utente è disconnesso
        #                      1 ----> Se l'utente è connesso
        #     'chatID': Valore controllato al primo accesso dopo una registrazione/disconnessione
        #     'userID': Dato dall'utente
        #     'logOutBackup' : " "
        # }
        self.sessionStatus = []
        #  Struct utile per gestire l'inserimento dei prodotti
        #  Normalmente la lista è vuota per aiutare la gestione degli errori
        # {
        #     'chatID':  ,
        #     'action': 'new'/'delete'/'stats'
        #     'product_type':
        #     'quantity':
        #     'roomID':

        # }
        self.productRequestStatus = []
        self.queueAlarms=[]
        # Per capire quando è possibile inserire un input da tastiera
        #{
        #     'chatID':
        #     'date':
        #     'requested':
        #     'mode':
        # }
        self.dateRequestedLeast = []
        self.dateRequestedMost = []
        #{
        #     'chatID':
        #     'th':
        # }
        self.threshold = []

#####################################################################################
#-------------MQTT------------------------------------------------------------------#
#####################################################################################
    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
    def follow(self):
        self.client.mySubscribe(self.topic)
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def notify(self,topic,msg,qos=2):
        payload=json.loads(msg)
        topic_splitted=topic.split('/')
        to_store_dict={}
        rangedDevice=['temperature','humidity','smoke']
        if payload['measure_type'] in rangedDevice:
            message = f"ALARM!!! Value out of range\nRoom: {payload['Room']}\nDevice: {topic_splitted[4]}\nSensor type: {payload['measure_type']}\nCRITICAL VALUE: {payload['value']}"
            to_store_dict=dict(chatID={payload['chatID']},msg=message)
            self.queueAlarms.append(to_store_dict)
        else:
            message = f"ALARM, BLACKOUT!!!\nRoom: {payload['Room']}\nDevice: {topic_splitted[4]}\nTime duration of blackout: {payload['value']}"
            to_store_dict=dict(chatID={payload['chatID']},msg=message)
            self.queueAlarms.append(to_store_dict)

#####################################################################################
#####################################################################################
    def sendCriticalMessage(self,chatID,msg):
        self.bot.sendMessage(chatID, text=msg)

    def on_chat_message(self, msg):
        #Flag per capire se il messaggio è una foto o del testo
        isPhoto= False
        isText= False
        message= 0
        #cancello il messaggio il messagio inviato dall'utente per evitare che lo editi
        # e che quindi impalli la coda di messaggi del BOT
        self.bot.deleteMessage(telepot.message_identifier(msg))
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if 'text' in msg:
            #se è un messaggio di testo aggiorna il flag e salva il body del messagio
            isText=True
            message = msg['text']

        else:
            if content_type == 'photo':
                # se è una foto aggiorna il flag e salva la foto in locale la foto facendo il download
                isPhoto = True
                self.bot.download_file(
                    msg['photo'][-1]['file_id'], './barcode.png')

        if isText:
            if message.startswith('/'):
                if message == "/start":
                    #inizializza il flag di Log-in sempre a false perchè
                    # se l'utente non si è registrato, e quindi non è presente
                    # nella lista sessionStatus non può accedere alla dashboard
                    logged = False
                    for status in self.sessionStatus:
                        # iterazione su sessionStatus per capire se il
                        # chatID del messaggio ricevuto è di un utente registrato
                        if status['chatID'] == chat_ID:
                            #se lo trovo controllo se l'user ha fatto il Log-in
                            # Se è loggato lo reindirizzo direttamente alla dashboard
                            # a cui può accedere
                            if status['Log_in_status'] == 1:
                                logged = True
                                #controllo se è un MANAGER o un WORKER
                                userID = status['userID']
                                isManager = userID.startswith('M_')
                                if isManager:
                                    self.ManagerRoutine(userID, chat_ID, False)
                                    break
                                else:
                                    self.WorkerRoutine(userID, chat_ID, False)
                                    break
                    if not logged:
                        #se non ho trovato la chatID nel sessionStatus
                        # lo rimando alla routine di registrazione
                        logged = False
                        self.startRoutine(chat_ID)
                else:
                    # se inserisce un comando /COMANDO diverso da /start lo avviso dell'errore
                    self.bot.sendMessage(chat_ID, text="Command not supported")
            else:
                if message.startswith('U_') or message.startswith('M_'):
                    # se il messaggio forwardato inizia con U_ o M_ è sicuramente in fase di registrazione
                    userIDs = []
                    found = False
                    registered = False
                    # prendo dal catalog la lista di Username abilitati
                    r=requests.get(f'{self.catalog_IP}/catalog/users')
                    body = json.dumps(r.json(), indent=4)
                    userDict = json.loads(body)
                    userList = userDict['userList']
                    for user in userList:
                        userIDs.append(user['userID'])
                    # controllo se l'username è presente nella lista presa dal catalog
                    if message in userIDs:
                        found = True
                        for status in self.sessionStatus:
                            if status['chatID'] == chat_ID:
                                if status['isRegister']:
                                    registered = True
                                else:
                                    status['userID'] = message
                                    status['isRegister'] = True
                                    body=json.dumps({'chatID':chat_ID})
                                    requests.put(url=f'{self.catalog_IP}/catalog/{message}/change_chatID',
                                                  data=body)
                    if found and not registered:
                        found = False
                        #Se trovo l'userID è valido e l'utente non si era già registrato in precendenza lo registro
                        text = f'Wonderful {message}, you signed-in succesfully, now click /start to see all functionalities of WareHouseBot'
                        self.bot.sendMessage(chat_ID, text=text)
                    elif not found:
                        # Se l'userID non è valido lo avverto
                        text = f'WRONG ID!!!\nPlease insert your userID to have access to all functionalities:'
                        self.bot.sendMessage(chat_ID, text=text)
                elif message.isdigit():
                    if len(self.dateRequestedMost) > 0:
                        # Se si deve trovare il più venduto
                        # Se si deve inserire mese o anno nella richiesta delle statistiche
                        for request in self.dateRequestedMost:
                            if request['chatID'] == chat_ID:
                                request['date'] = int(message)
                                if request['requested'] == 'month':
                                    # Month is requested
                                    if request['date'] < 1 or request['date'] > 12:
                                        text = "Insert a valid month number"
                                        self.bot.sendMessage(chat_ID, text=text)
                                    else:
                                        buttons = [[InlineKeyboardButton(text=f'Continue',
                                                                callback_data=f'most_month_products')]
                                        ]
                                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                                        text = "Click 'Continue' to go on"
                                        self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)
                                else:
                                    # Year is requested
                                    if request['date'] < 2020:
                                        text = "Insert a valid year number"
                                        self.bot.sendMessage(chat_ID, text=text)
                                    else:
                                        buttons = [[InlineKeyboardButton(text=f'Continue',
                                                                callback_data=f'most_year_products')]
                                        ]
                                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                                        text = "Click 'Continue' to go on"
                                        self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)
                    
                    elif len(self.dateRequestedLeast) > 0:
                        # Se si deve trovare il meno venduto
                        # Se si deve inserire mese o anno nella richiesta delle statistiche
                        for request in self.dateRequestedLeast:
                            if request['chatID'] == chat_ID:
                                request['date'] = int(message)
                                if request['requested'] == 'month':
                                    # Month is requested
                                    if request['date'] < 1 or request['date'] > 12:
                                        text = "Insert a valid month number"
                                        self.bot.sendMessage(chat_ID, text=text)
                                    else:
                                        buttons = [[InlineKeyboardButton(text=f'Continue',
                                                                callback_data=f'least_month_products')]
                                        ]
                                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                                        text = "Click 'Continue' to go on"
                                        self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)
                                else:
                                    # Year is requested
                                    if request['date'] < 2020:
                                        text = "Insert a valid year number"
                                        self.bot.sendMessage(chat_ID, text=text)
                                    else:
                                        buttons = [[InlineKeyboardButton(text=f'Continue',
                                                                callback_data=f'least_year_products')]
                                        ]
                                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                                        text = "Click 'Continue' to go on"
                                        self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

                    elif len(self.threshold) > 0:
                        # If some threshold input is needed
                        for request in self.threshold:
                            if request['chatID'] == chat_ID:
                                request['th'] = int(message)
                                buttons = [[InlineKeyboardButton(text=f'Continue',callback_data=f'get_th_products')]]
                                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                                text = "Click 'Continue' to go on"
                                self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

                    # Routine utile per l'inserimento del prodotto
                    # Per evitare che inserendo un numero in una parte a caso del bot esso si
                    # impalli controllo se è in atto una richiesta di inserimento/rimozione del prodotto
                    elif len(self.productRequestStatus) > 0:
                        for productReq in self.productRequestStatus:
                            if productReq['chatID'] == chat_ID:
                                quantity=int(message)
                                productReq['quantity'] = quantity
                                for status in self.sessionStatus:
                                    if status['chatID'] == chat_ID:
                                        userID = status['userID']
                                        self.roomRoutine(chat_ID, userID, 1)

                    else:
                        text = f'WRONG COMMAND!!!!'
                        self.bot.sendMessage(chat_ID, text=text)
                else:
                    text = f'WRONG COMMAND!!!!'
                    self.bot.sendMessage(chat_ID, text=text)
        elif isPhoto:
            # Routine utile per l'inserimento del prodotto
            # Per evitare che inserendo una foto in una parte a caso del bot esso si
            # impalli controllo se è in atto una richiesta di inserimento/rimozione del prodotto
            if len(self.productRequestStatus) > 0:
                barcode = BarcodeScanner.readBarcode()
                #controllo se il Barcode è stato letto correttamente
                if barcode == None:
                    text = f'Scan go wrong,please take a more clear shot!'
                    self.bot.sendMessage(chat_ID, text=text)

                else:
                    #trasformo il barcode in stringa per evitare errori nella request successiva
                    barcode = str(barcode)
                    # vedo se l'utente in questione avevo fatto una
                    # richiesta di inserimento/rimozione del prodotto
                    found= False
                    for productReq in self.productRequestStatus:
                        if productReq['chatID'] == chat_ID:
                            found=True
                            if 'quantity' in productReq.keys():
                                action = productReq['action']
                                roomID = productReq['roomID']
                                product_type= productReq['product_type']
                                if action == "delete":
                                    quantityRequested = productReq['quantity']
                                    r = requests.get(f"{self.database_stats_URL}/db/stored/{roomID}/{barcode}/all")
                                    body = json.dumps(r.json(), indent=4)
                                    productsDict = json.loads(body)
                                    productsList = productsDict['products']
                                    if len(productsList) > 0:
                                        quantityDB = 0
                                        for product in productsList:
                                            quantityDB += product['quantity']
                                        if quantityRequested > quantityDB:
                                            self.productRequestStatus.remove(productReq)
                                            text = f"Resource of this product in warehouse is not enough please click /start to go back to dashboard\n>Quantity MAX-->{quantityDB}\n>Barcode -->{barcode}"
                                            self.bot.sendMessage(chat_ID, text=text)
                                    else:
                                        self.productRequestStatus.remove(productReq)
                                        text = "PRODUCT NOT FOUND!!!"
                                        self.bot.sendMessage(chat_ID, text=text)



                                body = json.dumps({"product_ID": barcode, "quantity": quantityRequested,
                                                   "product_type": product_type})
                                if action=='delete':
                                    word='sold'
                                    r = requests.delete(url=f"{self.stored_products_IP}/db/{roomID}/{barcode}/{action}",
                                                     data=body)
                                    self.productRequestStatus.remove(productReq)
                                else:

                                    r = requests.put(url=f"{self.stored_products_IP}/db/{roomID}/{barcode}/{action}",
                                                     data=body)
                                    self.productRequestStatus.remove(productReq)
                                    word='added'
                                text = f"Successfull scan please click /start to go back to dashboard\nOverview transaction:\n>Quantity {word} -->{productReq['quantity']}\n>Barcode -->{barcode}"
                                self.bot.sendMessage(chat_ID, text=text)
                            else:
                                text = f"You jumped a passage,please insert quantity!!!"
                                self.bot.sendMessage(chat_ID, text=text)
                        else:
                            text = f'CONTENT NOT SUPPORTED IN THIS SECTION!!!!'
                            self.bot.sendMessage(chat_ID, text=text)
            else:
                text = f'CONTENT NOT SUPPORTED IN THIS SECTION!!!!'
                self.bot.sendMessage(chat_ID, text=text)



    def on_callback_query(self, msg):
        query_ID, chat_ID, query_data = telepot.glance(
            msg, flavor='callback_query')

        if query_data == 'accedi':
            found = False
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    found = True
                    userID = status['userID']
                    isManager = userID.startswith('M_')
                    status['Log_in_status'] = 1
            if found:
                if isManager:
                    self.ManagerRoutine(userID, chat_ID, True)
                else:
                    self.WorkerRoutine(userID, chat_ID, True)
            else:
                text = f'You must register to have access to all functionalities.'
                self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'registra':
            # {
            #     'isRegister':True/False,
            #     'Log_in_status':0 ----> Se l'utente è disconnesso
            #                      1 ----> Se l'utente è connesso
            #     'chatID': Valore controllato al primo accesso dopo una registrazione/disconnessione
            #     'userID': Dato dall'utente
            # }
            registered_user = []
            for status in self.sessionStatus:
                if status['isRegister']:
                    registered_user.append(status['chatID'])
            if chat_ID not in registered_user:
                registration_form = dict(
                    isRegister=False,
                    Log_in_status=0,
                    chatID=chat_ID,
                    userID=None)
                self.sessionStatus.append(registration_form)
                text = f'Please insert your userID to have access to all functionalities:'
                self.bot.sendMessage(chat_ID, text=text)
            else:
                text = f'You are already registered, click /start and then Log-in:'
                self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'Quit':
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    status['Log_in_status'] = 0
                    text = f'YOU SUCCESSFULL LOGOUT!!!'
                    self.bot.sendMessage(chat_ID, text=text)
        elif query_data == 'Statistics':
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    break
            self.roomRoutine(chat_ID, userID,0)

        elif query_data == 'Overview_owner':
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID=status['userID']
                    break
            r = requests.get(f'{self.catalog_IP}/catalog/rooms')
            body = json.dumps(r.json(), indent=4)
            roomDict = json.loads(body)
            r = requests.get(f'{self.catalog_IP}/catalog/{userID}/assigned_rooms')
            body = json.dumps(r.json(), indent=4)
            assignedDict = json.loads(body)
            rooms= roomDict['roomList']
            assignedRooms=assignedDict['assignedRoomIds']
            user_device_of_interest=[]
            message=""
            for room in rooms:
                if room['roomID'] in assignedRooms:
                    r = requests.get(f"{self.catalog_IP}/catalog/{room['roomID']}/users")
                    body = json.dumps(r.json(), indent=4)
                    userDict = json.loads(body)
                    users=userDict['user']
                    userToOutput=[]
                    devicesToOutput=[]
                    for user in users:
                        if user != userID:
                            userToOutput.append(user)
                    for device in room['devicesList']:
                        devicesToOutput.append(device['deviceID'])

                    dictTostore=dict(roomID=room['roomID'],users=userToOutput,devices=devicesToOutput)
                    user_device_of_interest.append(dictTostore)
            for item in user_device_of_interest:
                message=message+f"Room_ID:{item['roomID']}\nUsers assigned to this room:\n{item['users']}\nDevices contained:\n{item['devices']}\n"
            self.bot.sendMessage(chat_ID, text=message)

        elif query_data == 'Products_owner':
            # Define the buttons to retrieve the products statistics
            buttons = [[InlineKeyboardButton(text=f'Get all',
                                             callback_data=f'get_all_products'),
                        InlineKeyboardButton(text=f'Get sold',
                                             callback_data=f'get_sold_products'),
                        InlineKeyboardButton(text=f'Get stored',
                                             callback_data=f'get_stored_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_all_products':
            # Get all the products, both stored and sold
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            sold_products = d_data["products_sold"]
            stored_products = d_data["products_stored"]
            # Check if the result is correct:
            # list if correct
            # else -1
            if isinstance(sold_products, list) and isinstance(stored_products, list):
                text="Sold products: \n"
                for product in sold_products:
                    text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                text+="\n\nStored products: \n"
                for product in stored_products:
                    text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_sold_products':
            # Define buttons to retrieve sold products statistics
            buttons = [[InlineKeyboardButton(text=f'Get all products',
                                             callback_data=f'get_all_sold_products'),
                        InlineKeyboardButton(text=f'Statistics',
                                             callback_data=f'get_satistics_sold_products')],                     
                        [InlineKeyboardButton(text=f'Most sold products',
                                             callback_data=f'get_most_sold_products'),
                        InlineKeyboardButton(text=f'Least sold products',
                                             callback_data=f'get_least_sold_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_all_sold_products':
            # Get all the sold products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/sold/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            products = d_data["products"]
            # Check if the result is correct:
            # list if correct
            # else -1
            if isinstance(products, list):
                text="Sold products: \n"
                for product in products:
                    text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_satistics_sold_products':
            # Define the buttons for all the possible sold products statistics
            buttons = [[InlineKeyboardButton(text=f'Mean quantity',
                                             callback_data=f'mean_sold_products'),
                        InlineKeyboardButton(text=f'Total quantity',
                                             callback_data=f'total_sold_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'mean_sold_products':
            # Get the mean quantity of sold products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/statistics/mean/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            mean = d_data["mean"]
            # Check if the result is correct:
            # positive number if correct
            # else -1
            if mean != -1:
                text=f"Mean quantity of products sold: {mean}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'total_sold_products':
            # Get the total quantity of sold products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/statistics/total/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            total = d_data["total"]
            # Check if the result is correct:
            # positive number if correct
            # else -1
            if total != -1:
                text=f"Total quantity of products sold: {total}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_most_sold_products':
            # Define all the most sold products statistics buttons
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'most_overall_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'most_room_products')],
                        [InlineKeyboardButton(text=f'By month',
                                             callback_data=f'get_most_month'),
                        InlineKeyboardButton(text=f'By year',
                                             callback_data=f'get_most_year')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'most_overall_products':
            # Get the overall most sold products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/sold/most/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            products = d_data["products"]
            # Check if the result is correct:
            # list if correct
            # else -1
            if isinstance(products, list):
                text="Most sold products: \n"
                for product in products:
                    text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'most_room_products':
            # Get the most sold products in a given room
            productRequest = dict(chatID=chat_ID, action='most')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data == 'get_most_month':
            # Ask the user to insert the month
            dictTostore=dict(chatID = chat_ID, date = None, requested = 'month')
            self.dateRequestedMost.append(dictTostore)
            text = "Please insert month number:"
            self.bot.sendMessage(chat_ID, text=text)
            
        elif query_data == 'get_most_year':
            # Ask the user to insert the year
            dictTostore=dict(chatID = chat_ID, date = None, requested = 'year')
            self.dateRequestedMost.append(dictTostore)
            text = "Please insert year number:"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data.split(',')[0] == 'most_sold':
            # Get the most sold products in a given room
            to_remove = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'most':
                    if productRequest['chatID']== chat_ID:
                        to_remove = productRequest
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/sold/{roomID}/most/all')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Most sold products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'most_month_products':
            # Define all the most sold products by month statistics buttons
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'overall_most_month_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'room_most_month_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'overall_most_month_products':
            # Get the most sold products in a given month
            to_remove = None
            for request in self.dateRequestedMost:
                if request['requested'] == 'month':
                    if request['chatID'] == chat_ID:
                        to_remove = request
                        # Get the month wanted
                        month = request['date']
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/sold/most/month/all?month={month}')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Most sold products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.dateRequestedMost.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'room_most_month_products':
            # Get the most sold products in a given month in a given room
            productRequest = dict(chatID=chat_ID, action='most_month')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'return_room_most_month_products':
            # Get the most sold products in a given month in a given room
            to_remove_2 = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'most_month':
                    if productRequest['chatID']== chat_ID:
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        to_remove_2 = productRequest
                        to_remove = None
                        for request in self.dateRequestedMost:
                            if request['requested'] == 'month':
                                if request['chatID'] == chat_ID:
                                    to_remove = request
                                    # Get the month wanted
                                    month = request['date']
                                    # Request to Statistics_products server
                                    r_data = requests.get(f'{self.database_stats_URL}/db/sold/{roomID}/most/month/all?month={month}')
                                    j_data = json.dumps(r_data.json(),indent=4)
                                    d_data = json.loads(j_data)
                                    products = d_data["products"]
                                    # Check if the result is correct:
                                    # list if correct
                                    # else -1
                                    if isinstance(products, list):
                                        text="Most sold products: \n"
                                        for product in products:
                                            text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                                    else:
                                        text="Some error occurred!"
                                    text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove_2)
            self.dateRequestedMost.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'most_year_products':
            # Define all the most products by year statistics buttons
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'overall_most_year_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'room_most_year_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'overall_most_year_products':
            # Get the most sold products in a given year
            to_remove = None
            for request in self.dateRequestedMost:
                if request['requested'] == 'year':
                    if request['chatID'] == chat_ID:
                        to_remove = request
                        # Get the year wanted
                        year = request['date']
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/sold/most/year/all?year={year}')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Most sold products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.dateRequestedMost.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'room_most_year_products':
            # Get the most sold products in a given year in a given room
            productRequest = dict(chatID=chat_ID, action='most_year')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'return_room_most_year_products':
            # Get the most sold products in a given year in a given room
            to_remove_2 = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'most_year':
                    if productRequest['chatID']== chat_ID:
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        to_remove_2 = productRequest
                        to_remove = None
                        for request in self.dateRequestedMost:
                            if request['requested'] == 'year':
                                if request['chatID'] == chat_ID:
                                    to_remove = request
                                    # Get the year wanted
                                    year = request['date']
                                    # Request to Statistics_products server
                                    r_data = requests.get(f'{self.database_stats_URL}/db/sold/{roomID}/most/year/all?year={year}')
                                    j_data = json.dumps(r_data.json(),indent=4)
                                    d_data = json.loads(j_data)
                                    products = d_data["products"]
                                    # Check if the result is correct:
                                    # list if correct
                                    # else -1
                                    if isinstance(products, list):
                                        text="Most sold products: \n"
                                        for product in products:
                                            text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                                    else:
                                        text="Some error occurred!"
                                    text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove_2)
            self.dateRequestedMost.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_least_sold_products':
            # Define all the least sold products statistics buttons
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'least_overall_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'least_room_products')],
                        [InlineKeyboardButton(text=f'By month',
                                             callback_data=f'get_least_month'),
                        InlineKeyboardButton(text=f'By year',
                                             callback_data=f'get_least_year')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'least_overall_products':
            # Get the overall least sold products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/sold/least/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            products = d_data["products"]
            # Check if the result is correct:
            # list if correct
            # else -1
            if isinstance(products, list):
                text="Least sold products: \n"
                for product in products:
                    text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'least_room_products':
            # Get the least sold products in a given room
            productRequest = dict(chatID=chat_ID, action='least')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data == 'get_least_month':
            # Ask the user to insert the month
            dictTostore=dict(chatID = chat_ID, date = None, requested = 'month')
            self.dateRequestedLeast.append(dictTostore)
            text = "Please insert month number:"
            self.bot.sendMessage(chat_ID, text=text)
            
        elif query_data == 'get_least_year':
            # Ask the user to insert the year
            dictTostore=dict(chatID = chat_ID, date = None, requested = 'year')
            self.dateRequestedLeast.append(dictTostore)
            text = "Please insert year number:"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data.split(',')[0] == 'least_sold':
            # Get the least sold products in a given room
            to_remove = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'least':
                    if productRequest['chatID']== chat_ID:
                        to_remove = productRequest
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/sold/{roomID}/least/all')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Least sold products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'least_month_products':
            # Define all the least sold products by month statistics buttons
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'overall_least_month_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'room_least_month_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'overall_least_month_products':
            # Get the least sold products in a given month
            to_remove = None
            for request in self.dateRequestedLeast:
                if request['requested'] == 'month':
                    if request['chatID'] == chat_ID:
                        to_remove = request
                        # Get the month wanted
                        month = request['date']
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/sold/least/month/all?month={month}')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Least sold products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.dateRequestedLeast.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'room_least_month_products':
            # Get the least sold products in a given month in a given room
            productRequest = dict(chatID=chat_ID, action='least_month')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'return_room_least_month_products':
            # Get the least sold products in a given month in a given room
            to_remove_2 = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'least_month':
                    if productRequest['chatID']== chat_ID:
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        to_remove_2 = productRequest
                        to_remove = None
                        for request in self.dateRequestedLeast:
                            if request['requested'] == 'month':
                                if request['chatID'] == chat_ID:
                                    to_remove = request
                                    # Get the month wanted
                                    month = request['date']
                                    # Request to Statistics_products server
                                    r_data = requests.get(f'{self.database_stats_URL}/db/sold/{roomID}/least/month/all?month={month}')
                                    j_data = json.dumps(r_data.json(),indent=4)
                                    d_data = json.loads(j_data)
                                    products = d_data["products"]
                                    # Check if the result is correct:
                                    # list if correct
                                    # else -1
                                    if isinstance(products, list):
                                        text="Least sold products: \n"
                                        for product in products:
                                            text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                                    else:
                                        text="Some error occurred!"
                                    text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove_2)
            self.dateRequestedLeast.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'least_year_products':
            # Define all the least sold products by year statistics buttons
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'overall_least_year_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'room_least_year_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'overall_least_year_products':
            # Get the least sold products in a given year
            to_remove = None
            for request in self.dateRequestedLeast:
                if request['requested'] == 'year':
                    if request['chatID'] == chat_ID:
                        to_remove = request
                        # Get the year wanted
                        year = request['date']
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/sold/least/year/all?year={year}')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Least sold products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.dateRequestedLeast.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'room_least_year_products':
            # Get the least sold products in a given year in a given room
            productRequest = dict(chatID=chat_ID, action='least_year')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'return_room_least_year_products':
            # Get the least sold products in a given year in a given room
            to_remove_2 = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'least_year':
                    if productRequest['chatID']== chat_ID:
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        to_remove_2 = productRequest
                        to_remove = None
                        for request in self.dateRequestedLeast:
                            if request['requested'] == 'year':
                                if request['chatID'] == chat_ID:
                                    to_remove = request
                                    # Get the year wanted
                                    year = request['date']
                                    # Request to Statistics_products server
                                    r_data = requests.get(f'{self.database_stats_URL}/db/sold/{roomID}/least/year/all?year={year}')
                                    j_data = json.dumps(r_data.json(),indent=4)
                                    d_data = json.loads(j_data)
                                    products = d_data["products"]
                                    # Check if the result is correct:
                                    # list if correct
                                    # else -1
                                    if isinstance(products, list):
                                        text="Least sold products: \n"
                                        for product in products:
                                            text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                                    else:
                                        text="Some error occurred!"
                                    text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove_2)
            self.dateRequestedLeast.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_stored_products':
            # Define all the statistics buttons related to the stored products
            buttons = [[InlineKeyboardButton(text=f'Get all products',
                                             callback_data=f'get_all_stored_products'),
                        InlineKeyboardButton(text=f'Statistics',
                                             callback_data=f'get_satistics_stored_products')],                     
                        [InlineKeyboardButton(text=f'Specific product',
                                             callback_data=f'get_specific_products'),
                        InlineKeyboardButton(text=f'Small amount',
                                             callback_data=f'get_small_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)
        
        elif query_data == 'get_all_stored_products':
            # Define all the statistics buttons related to retrieving all the stored products
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'get_overall_all_stored_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'get_room_all_stored_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_overall_all_stored_products':
            # Retrieve all the stored products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/stored/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            products = d_data["products"]
            # Check if the result is correct:
            # list if correct
            # else -1
            if isinstance(products, list):
                text="Stored products: \n"
                for product in products:
                    text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_room_all_stored_products':
            # Retrieve all the stored products within a given room
            productRequest = dict(chatID=chat_ID, action='stored')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'all_stored_by_room_products':
            # Retrieve all the stored products within a given room
            to_remove = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'stored':
                    if productRequest['chatID']== chat_ID:
                        to_remove = productRequest
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/stored/{roomID}/all')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        products = d_data["products"]
                        # Check if the result is correct:
                        # list if correct
                        # else -1
                        if isinstance(products, list):
                            text="Stored products: \n"
                            for product in products:
                                text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
                        self.productRequestStatus.remove(to_remove)
                        self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_satistics_stored_products':
            # Define all the available statistics on the stored products
            buttons = [[InlineKeyboardButton(text=f'Total number',
                                             callback_data=f'get_total_number_products'),
                        InlineKeyboardButton(text=f'Mode',
                                             callback_data=f'get_mode_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_total_number_products':
            # Define all the available statistics on the total number of stored products
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'get_overall_total_number_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'get_room_overall_total_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_overall_total_number_products':
            # Retrieve the overall number of stored products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db//statistics/count/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            count = d_data["count"]
            # Check if the result is correct:
            # positive number if correct
            # else -1
            if count != -1:
                text=f"Total number of products stored: {count}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_room_overall_total_products':
            # Retrieve the overall number of stored products in a given room
            productRequest = dict(chatID=chat_ID, action='count')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)
        
        elif query_data.split(',')[0] == 'overall_total_specific_room_products':
            # Retrieve the overall number of stored products in a given room
            to_remove = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'count':
                    if productRequest['chatID']== chat_ID:
                        to_remove = productRequest
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/statistics/count/{roomID}/all')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        count = d_data["count"]
                        # Check if the result is correct:
                        # positive number if correct
                        # else -1
                        if count != -1:
                            text=f"Total number of products stored: {count}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
                        self.productRequestStatus.remove(to_remove)
                        self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_mode_products':
            # Define all the available statistics on the mode of the stored products
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'get_overall_mode_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'get_room_mode_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_overall_mode_products':
            # Retrieve the overall mode of the stored products
            # Request to Statistics_products server
            r_data = requests.get(f'{self.database_stats_URL}/db/statistics/mode/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            mode = d_data["mode"]
            # Check if the result is correct:
            # positive number if correct
            # else -1
            if mode != -1:
                text=f"Mean quantity of products sold: {mode}\n"
            else:
                text="Some error occurred!"
            text+="\n\n Press /start to return to the dashboard"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_room_mode_products':
            # Retrieve the overall mode of the stored products in a given room
            productRequest = dict(chatID=chat_ID, action='mode')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'mode_specific_room_products':
            # Retrieve the overall mode of the stored products in a given room
            to_remove = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'mode':
                    if productRequest['chatID']== chat_ID:
                        to_remove = productRequest
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        # Request to Statistics_products server
                        r_data = requests.get(f'{self.database_stats_URL}/db/statistics/mode/{roomID}/all')
                        j_data = json.dumps(r_data.json(),indent=4)
                        d_data = json.loads(j_data)
                        mode = d_data["mode"]
                        # Check if the result is correct:
                        # positive number if correct
                        # else -1
                        if mode != -1:
                            text=f"Mean quantity of products sold: {mode}\n"
                        else:
                            text="Some error occurred!"
                        text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_specific_products':
            # Retrieve the info about some specific product in a given room
            productRequest = dict(chatID=chat_ID, action='product')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'insert_specific_product':
            to_remove = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'product':
                    if productRequest['chatID']== chat_ID:
                        to_remove = productRequest
                        # Save the correct wanted roomID
                        roomID = query_data.split(',')[1]
            # Retrieve all the products in the wanted room
            r_data = requests.get(f'{self.database_stats_URL}/db/stored/{roomID}/all')
            j_data = json.dumps(r_data.json(),indent=4)
            d_data = json.loads(j_data)
            products = d_data["products"]
            # Check if the result is correct:
            # list if correct
            # else -1
            # flag is used to understand if this function has already been called
            # flag=1 : never called
            # flag=0 : called once
            flag = query_data.split(',')[2]
            if isinstance(products, list) and flag == 'flag=1':
                # This function has never been called before
                inline = []
                buttons = []
                cnt = 0
                for product in products:
                    # For every product append a button with its ID
                    text = product["product_ID"]
                    inline.append(InlineKeyboardButton(text=text, callback_data='insert_specific_product'
                                                       +','+roomID+','+'flag=0'+','+text))
                    cnt = cnt + 1
                    if cnt == 4:
                        buttons.append(inline)
                        inline = []
                        cnt = 0
                if cnt < 4:
                    buttons.append(inline)
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text='Choose a device:',reply_markup=keyboard)
            elif isinstance(products, list) and flag == 'flag=0':
                # This function has already been called once
                # Get product ID
                productID = query_data.split(',')[3]
                # Print the required product
                text = "Requested product:\n"
                for product in products:
                    if product["product_ID"] == productID:
                        text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                text+="\n\n Press /start to return to the dashboard"
                self.productRequestStatus.remove(to_remove)
                self.bot.sendMessage(chat_ID, text=text)
            else:
                text="Some error occurred!"
                text+="\n\n Press /start to return to the dashboard"
                self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_small_products':
             # Ask the user to insert the threshold
            dictTostore=dict(chatID = chat_ID, th = None)
            self.threshold.append(dictTostore)
            text = "Please insert threshold number:"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_th_products':
            # Create buttons to retrieve all the products under a certain threshold
            buttons = [[InlineKeyboardButton(text=f'Overall',
                                             callback_data=f'get_overall_th_products'),
                        InlineKeyboardButton(text=f'By room',
                                             callback_data=f'get_room_th_products')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the statistics to check:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'get_overall_th_products':
            # Retrieve all the products that are under some threshold
            to_remove = None
            for request in self.threshold:
                if request['chatID'] == chat_ID:
                    to_remove = request
                    # Get the threshold wanted
                    threshold = request['th']
                    # Request to Statistics_products server
                    r_data = requests.get(f'{self.database_stats_URL}/db/stored/threshold/all?th={threshold}')
                    j_data = json.dumps(r_data.json(),indent=4)
                    d_data = json.loads(j_data)
                    products = d_data["products"]
                    # Check if the result is correct:
                    # list if correct
                    # else -1                      
                    if isinstance(products, list):
                        text="Products under the selected quantity: \n"
                        for product in products:
                            text += f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                    else:
                        text="Some error occurred!"
                    text+="\n\n Press /start to return to the dashboard"
            self.threshold.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'get_room_th_products':
            # Retrieve all the products that are under some threshold in a given room
            productRequest = dict(chatID=chat_ID, action='th')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    # Call roomRoutine for generate a button for each room
                    # To find the wanted room
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data.split(',')[0] == 'th_specific_room_products':
            # Retrieve all the products that are under some threshold in a given room
            to_remove_2 = None
            for productRequest in self.productRequestStatus:
                if productRequest['action'] == 'th':
                    if productRequest['chatID']== chat_ID:
                        # Get the roomID wanted
                        roomID = query_data.split(',')[1]
                        to_remove_2 = productRequest
                        to_remove = None
                        for request in self.threshold:
                            if request['chatID'] == chat_ID:
                                to_remove = request
                                # Get the threshold wanted
                                threshold = request['th']
                                # Request to Statistics_products server
                                r_data = requests.get(f'{self.database_stats_URL}/db/stored/{roomID}/threshold/all?th={threshold}')
                                j_data = json.dumps(r_data.json(),indent=4)
                                d_data = json.loads(j_data)
                                products = d_data["products"]
                                # Check if the result is correct:
                                # list if correct
                                # else -1
                                if isinstance(products, list):
                                    text="Products under the selected quantity: \n"
                                    for product in products:
                                        text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                                else:
                                    text="Some error occurred!"
                                text+="\n\n Press /start to return to the dashboard"
            self.productRequestStatus.remove(to_remove_2)
            self.threshold.remove(to_remove)
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'Product_av':
            productRequest = dict(chatID=chat_ID, action='stats')
            self.productRequestStatus.append(productRequest)
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    self.roomRoutine(chat_ID, userID, 1)

        elif query_data == 'Product_stored':
            for productRequest in self.productRequestStatus:
                if productRequest['chatID']== chat_ID:
                    roomID = productRequest['roomID']
                    r = requests.get(f"{self.database_stats_URL}/db/stored/{roomID}/all")
                    body = json.dumps(r.json(), indent=4)
                    productsDict = json.loads(body)
                    productsList = productsDict['products_stored']
                    text=""
                    for product in productsList:
                        text+=f"Product ID : {product['product_ID']}\nQuantity : {product['quantity']}\n"
                    text+="\n\n Press \start to return to the dashboard"
                    self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)


        elif query_data == 'Manage_product':
            buttons = [[InlineKeyboardButton(text=f'Insert new products🟩',
                                             callback_data=f'Insert_product'),
                        InlineKeyboardButton(text=f'Remove products🟥',
                                             callback_data=f'Remove_product')]
                       ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text= "Select the action to apply:"
            self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

        elif query_data == 'Product_scan':
            text = "Please scan product :"
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == 'Remove_product':
            productRequest = dict(chatID=chat_ID, action='delete')
            self.productRequestStatus.append(productRequest)
            text = "Please insert the quantity of the product that you want to remove:"
            self.bot.sendMessage(chat_ID, text=text)
        elif query_data == 'Insert_product':
            productRequest= dict(chatID=chat_ID,action='new')
            self.productRequestStatus.append(productRequest)
            text = "Please insert the quantity of the product that you want to add :"
            self.bot.sendMessage(chat_ID, text=text)


        elif query_data[0:2] == 'R_':
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    break
            roomID = query_data
            dm = DailyMonitor(roomID,self.catalog_IP)
            msg = dm.data_retrieve()
            self.bot.sendMessage(chat_ID, text=msg)


    def ManagerRoutine(self, userID, chat_ID, flag):
        buttons = [[InlineKeyboardButton(text=f'Statistics📊',
                                         callback_data=f'Statistics'),
                    InlineKeyboardButton(text=f'Overview 🚨',
                                         callback_data=f'Overview_owner')],
                   [InlineKeyboardButton(text=f'Products 🧮',
                                         callback_data=f'Products_owner'),
                    InlineKeyboardButton(text=f'Quit❌',
                                         callback_data=f'Quit')]
                   ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        if flag:
            text = f'YOU SUCCESSFULL LOGIN!!!\nWelcome back {userID}, here the dashboard : '
        else:
            text = f'Welcome back {userID}, here the dashboard : '

        self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

    def WorkerRoutine(self, userID, chat_ID, flag):
        buttons = [[InlineKeyboardButton(text=f'Statistics📊',
                                         callback_data=f'Statistics'),
                    InlineKeyboardButton(text=f'Products available✅',
                                         callback_data=f'Prod_av')],
                   [InlineKeyboardButton(text=f'Manage Products ↔️',
                                         callback_data=f'Manage_product'),
                    InlineKeyboardButton(text=f'Quit❌',
                                         callback_data=f'Quit')]
                   ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        if flag:
            text = f'YOU SUCCESSFULL LOGIN!!!\nWelcome back {userID}, here the dashboard : '
        else:
            text = f'Welcome back {userID}, here the dashboard : '
        self.bot.sendMessage(chat_ID, text=text, reply_markup=keyboard)

    def startRoutine(self, chat_ID):
        welcome_menu = "Hi this is the access pannel of WareHouse Manager!!!\nIf you are a new you can register,if you are already register give a look on the statistics of your Warehouse!!!"
        buttons = [[InlineKeyboardButton(text=f'Log In🤙🏻',
                                         callback_data=f'accedi'),
                    InlineKeyboardButton(text=f'Register 💪🏻',
                                         callback_data=f'registra')],
                   ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text=welcome_menu,
                             reply_markup=keyboard)

    def roomRoutine(self, chat_ID, userID, routineContext):

        # Se routine context: --->0 Allora si riferisce alla routine delle statistiche dei device
        #                     --->1 Allora si riferisce a routine di gestione dei prodotti
        #                     --->2 Allora si riferisce alle statistiche dei prodotti

        r = requests.get(f'{self.catalog_IP}/catalog/rooms')
        body = json.dumps(r.json(), indent=4)
        roomDict= json.loads(body)
        r = requests.get(f'{self.catalog_IP}/catalog/{userID}/assigned_rooms')
        body = json.dumps(r.json(), indent=4)
        assignedDict = json.loads(body)
        roomsList = roomDict['roomList']
        assignedRooms = assignedDict['assignedRoomIds']
        inline = []
        buttons = []
        cnt = 0

        if routineContext == 0:
            for room in roomsList:
                if room['roomID'] in assignedRooms:
                    if room['product_type'] == '00':
                        emoji = '❄'
                    elif room['product_type'] == '01':
                        emoji = '💧'
                    elif room['product_type'] == '10':
                        emoji = '🔥'
                    cnt = cnt + 1
                    ID = room['roomID']
                    text = f'{ID} {emoji}'
                    inline.append(InlineKeyboardButton(text=text, callback_data=ID))
                    if cnt == 4:
                        buttons.append(inline)
                        inline = []
                        cnt = 0
            if cnt < 4:
                buttons.append(inline)


            buttons.append([InlineKeyboardButton(text='BACK⏪', callback_data='accedi')])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Choose a room:',
                                 reply_markup=keyboard)
        elif routineContext == 1:
            for room in roomsList:
                if room['roomID'] in assignedRooms:
                    if room['product_type'] == '00':
                        emoji = '❄'
                    elif room['product_type'] == '01':
                        emoji = '💧'
                    elif room['product_type'] == '11':
                        emoji = '🔥'
                    cnt = cnt + 1
                    ID = room['roomID']
                    text = f'{ID} {emoji}'
                    for productReq in self.productRequestStatus:
                        if productReq['chatID'] == chat_ID:
                            productReq['product_type'] = room['product_type']
                            productReq['roomID'] = room['roomID']
                        if productReq['action'] == 'stats':
                            inline.append(InlineKeyboardButton(text=text, callback_data='Product_stored'))
                        elif productReq['action'] == 'most':
                            inline.append(InlineKeyboardButton(text=text, callback_data='most_sold'+','+room['roomID']))
                        elif productReq['action'] =='most_month':
                            inline.append(InlineKeyboardButton(text=text, callback_data='return_room_most_month_products'+','+room['roomID']))
                        elif productReq['action'] == 'most_year':
                            inline.append(InlineKeyboardButton(text=text, callback_data='return_room_most_year_products'+','+room['roomID']))
                        elif productReq['action'] == 'least':
                            inline.append(InlineKeyboardButton(text=text, callback_data='least_sold'+','+room['roomID']))
                        elif productReq['action'] =='least_month':
                            inline.append(InlineKeyboardButton(text=text, callback_data='return_room_least_month_products'+','+room['roomID']))
                        elif productReq['action'] == 'least_year':
                            inline.append(InlineKeyboardButton(text=text, callback_data='return_room_least_year_products'+','+room['roomID']))
                        elif productReq['action'] == 'count':
                            inline.append(InlineKeyboardButton(text=text, callback_data='overall_total_specific_room_products'+','+room['roomID']))
                        elif productReq['action'] == 'mode':
                            inline.append(InlineKeyboardButton(text=text, callback_data='mode_specific_room_products'+','+room['roomID']))
                        elif productReq['action'] == 'stored':
                            inline.append(InlineKeyboardButton(text=text, callback_data='all_stored_by_room_products'+','+room['roomID']))
                        elif productReq['action'] == 'product':
                            inline.append(InlineKeyboardButton(text=text, callback_data='insert_specific_product'+','+room['roomID']+','+'flag=1'))
                        elif productReq['action'] == 'th':
                            inline.append(InlineKeyboardButton(text=text, callback_data='th_specific_room_products'+','+room['roomID']))
                        else:
                            inline.append(InlineKeyboardButton(text=text, callback_data='Product_scan'))

                    if cnt == 4:
                        buttons.append(inline)
                        inline = []
                        cnt = 0
            if cnt < 4:
                buttons.append(inline)



            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Choose a room:',
                                 reply_markup=keyboard)



if __name__ == "__main__":
    APIs = json.load(open("Settings.json"))
    catalogIP=APIs['catalogIP']
    r = requests.get(f'{catalogIP}/catalog/Telegram')
    body = json.dumps(r.json(), indent=4)
    TelegramDict = json.loads(body)
    conf = TelegramDict['Telegram']
    topic= conf['mqttTopic']
    broker = conf['brokerIP']
    port = conf['brokerPort']
    token = "1752637871:AAFRIWExGLSoOuqKc74RZG2ivI3ZZ85Xkrk"
    bot = WareBot(token,topic,broker,port,APIs)
    bot.run()
    bot.follow()
    while True:
        if len(bot.queueAlarms) > 0:
            retrivedDict=bot.queueAlarms.pop(0)
            for status in bot.sessionStatus:
                if status['chatID']==retrivedDict['chatID']:
                    if status['Log_in_status'] == 1:
                        bot.sendCriticalMessage(retrivedDict['chatID'], retrivedDict['msg'])
                    else:
                        if 'logOutBackup' not in status.keys():
                            status['logOutBackup']="Welcome back!!!\nWhen you  logged out you received this warnings:\n"
                            status['logOutBackup']+=retrivedDict['msg']
                        else:
                            status['logOutBackup'] += retrivedDict['msg']

        for status in bot.sessionStatus:
            if status['Log_in_status']==1 and ('logOutBackup' in status.keys()):
                bot.sendCriticalMessage(status['chatID'], status['logOutBackup'])
                del status['logOutBackup']

    bot.end()
