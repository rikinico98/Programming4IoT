import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import BarcodeScanner
from MyMQTT import *
import requests
import DailyMonitor

class WareBot:


    def __init__(self, token,baseTopic,broker,port):
        #Definisco il nome del client, topic, e MyMqtt object per la registrazione MQTT
        self.clientID = 'Bot_Telegram_Sub'
        self.topic = baseTopic
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
        # }
        self.sessionStatus = []
        #  Struct util per gestire l'inserimento dei prodotti
        #  Normalmente la lista è vuota per aiutare la gestione degli errori
        # {
        #     'chatID':  ,
        #     'action': 'new'/'delete'
        #     'barcode':
        #     'product_type':
        #     'quantity':

        # }
        self.productRequestStatus = []
        self.queueAlarms=[]

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
            message = f"ALARM, BLACKOUT!!!\nRoom: {payload['Room']}\nDevice: {topic_splitted[4]}"
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
                    r=requests.get('http://127.0.0.1:8070/catalog/users')
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
                                    requests.put(url=f'http://127.0.0.1:8070/catalog/{message}/change_chatID',
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
                    # Routine utile per l'inserimento del prodotto
                    # Per evitare che inserendo un numero in una parte a caso del bot esso si
                    #impalli controllo se è in atto una richiesta di inserimento/rimozione del prodotto
                    if len(self.productRequestStatus) > 0:
                        for productReq in self.productRequestStatus:
                            if productReq['chatID'] == chat_ID:
                                productReq['quantity'] = int(message)
                                for status in self.sessionStatus:
                                    if status['chatID'] == chat_ID:
                                        userID = status['userID']
                                        self.roomRoutine(chat_ID, userID,1)

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
                    # vedo se l'utente in questione avevo fatto una
                    # richiesta di inserimento/rimozione del prodotto
                    for productReq in self.productRequestStatus:
                        if productReq['chatID'] == chat_ID:
                            if 'quantity' in productReq.keys():
                                productReq['barcode'] = barcode
                                print(productReq)
                                self.productRequestStatus.remove(productReq)
                                text = f"Successfull scan please click /start to go back to dashboard\nOverview transaction:\n>Quantity -->{productReq['quantity']}\n>Barcode -->{barcode}"
                                self.bot.sendMessage(chat_ID, text=text)
                            else:
                                text = f"You jumped a passage,please insert quantity!!!"
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
            r = requests.get('http://127.0.0.1:8070/catalog/rooms')
            body = json.dumps(r.json(), indent=4)
            roomDict = json.loads(body)
            r = requests.get(f'http://127.0.0.1:8070/catalog/{userID}/assigned_rooms')
            body = json.dumps(r.json(), indent=4)
            assignedDict = json.loads(body)
            rooms= roomDict['roomList']
            assignedRooms=assignedDict['assignedRoomIds']
            user_device_of_interest=[]
            message=""
            for room in rooms:
                if room['roomID'] in assignedRooms:
                    r = requests.get(f"http://127.0.0.1:8070/catalog/{room['roomID']}/users")
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
            pass
        elif query_data == 'Product_av':
            pass
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
            dm = DailyMonitor(roomID)
            msg = dm.data_retrieve()
            self.bot.sendMessage(chat_ID, text=msg)

        # elif query_data[0:2] == 'D_':
        #     pass



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

        # If routine context: --->0 Allora si riferisce alla routine delle statistiche dei device
        #                     --->1 Allora si riferisce alla routine dellinserimento dei prodotti

        r = requests.get('http://127.0.0.1:8070/catalog/rooms')
        body = json.dumps(r.json(), indent=4)
        roomDict= json.loads(body)
        r = requests.get(f'http://127.0.0.1:8070/catalog/{userID}/assigned_rooms')
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
                    elif room['product_type'] == '10':
                        emoji = '🔥'
                    cnt = cnt + 1
                    ID = room['roomID']
                    text = f'{ID} {emoji}'
                    for productReq in self.productRequestStatus:
                        if productReq['chatID'] == chat_ID:
                            productReq['product_type'] = room['product_type']
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



    # def deviceRoutine(self, chat_ID, userID, roomID):
    #     r = requests.get('http://127.0.0.1:8070/catalog/rooms')
    #     body = json.dumps(r.json(), indent=4)
    #     roomDict= json.loads(body)
    #     r = requests.get(f'http://127.0.0.1:8070/catalog/{userID}/assigned_rooms')
    #     body = json.dumps(r.json(), indent=4)
    #     assignedDict = json.loads(body)
    #     roomsList = roomDict['roomList']
    #     assignedRooms = assignedDict['assignedRoomIds']
    #     inline = []
    #     buttons = []
    #     cnt = 0
    #     for room in roomsList:
    #         if room['roomID'] == roomID:
    #             for device in room['devicesList']:
    #                 cnt = cnt + 1
    #                 ID_room = room['roomID']
    #                 ID_device = device['deviceID']
    #                 text = f'{ID_device}'
    #                 ID = f'{ID_device}+{ID_room}'
    #                 inline.append(
    #                     InlineKeyboardButton(
    #                         text=text, callback_data=ID))
    #                 if cnt == 4:
    #                     buttons.append(inline)
    #                     inline = []
    #                     cnt = 0
    #             if cnt < 4:
    #                 buttons.append(inline)
    #         break
    #     buttons.append([InlineKeyboardButton(text='BACK⏪', callback_data='Statistics')])
    #
    #     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    #     self.bot.sendMessage(chat_ID, text='Choose a  device',
    #                          reply_markup=keyboard)


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    topic= conf['mqttTopic']
    broker = conf['brokerIP']
    port = conf['brokerPort']
    token = conf["telegramToken"]
    bot = WareBot(token,topic,broker,port)
    bot.run()
    bot.follow()
    while True:
        if len(bot.queueAlarms) > 0:
            retrivedDict=bot.queueAlarms.pop(0)
            bot.sendCriticalMessage(retrivedDict['chatID'],retrivedDict['msg'])

    bot.end()
