import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
import cherrypy

DICT = {'roomList': [{"roomID": "R_001",
                      "devicesList": [
                          {"deviceID": "D_001", "deviceName": "R1P1", "measureType": "AAA",
                                       "availableServices": ["MQTT", "REST"], "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao11",
                                            "topic": ["mio/prova1", "mio/prova11"]},
                                           {"serviceType": "REST", "serviceIP": "ciao12", "topic": []}
                                       ]},
                          {"deviceID": "D_002", "deviceName": "R1P2", "measureType": "BBB",
                                       "availableServices": ["MQTT", "REST"],
                                       "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao21",
                                            "topic": ["mio/prova2", "mio/prova22"]},
                                           {"serviceType": "REST", "serviceIP": "ciao22", "topic": []}
                                       ]},
                          {"deviceID": "D_003", "deviceName": "R1P3", "measureType": "CCC",
                                       "availableServices": ["MQTT", "REST"],
                                       "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao31",
                                            "topic": ["mio/prova3", "mio/prova33"]},
                                           {"serviceType": "REST", "serviceIP": "ciao32", "topic": []}
                                       ]},
                          {"deviceID": "D_004", "deviceName": "R1P4", "measureType": "DDD",
                                       "availableServices": ["MQTT", "REST"], "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao41",
                                            "topic": ["mio/prova4", "mio/prova44"]},
                                           {"serviceType": "REST", "serviceIP": "ciao42", "topic": []}
                                       ]}
                      ],
                      "product_type": "10"},
                     {"roomID": "R_002",
                      "devicesList": [
                          {"deviceID": "D_005", "deviceName": "R2P1", "measureType": "AAA",
                                       "availableServices": ["MQTT", "REST"],
                                       "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao51",
                                            "topic": ["mio/prova5", "mio/prova55"]},
                                           {"serviceType": "REST", "serviceIP": "ciao52", "topic": []}
                                       ]},
                          {"deviceID": "D_006", "deviceName": "R2P2", "measureType": "BBB",
                                       "availableServices": ["MQTT", "REST"],
                                       "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao61",
                                            "topic": ["mio/prova6", "mio/prova66"]},
                                           {"serviceType": "REST", "serviceIP": "ciao62", "topic": []}
                                       ]},
                          {"deviceID": "D_007", "deviceName": "R2P3", "measureType": "CCC",
                                       "availableServices": ["MQTT", "REST"],
                                       "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao71",
                                            "topic": ["mio/prova7", "mio/prova77"]},
                                           {"serviceType": "REST", "serviceIP": "ciao72", "topic": []}
                                       ]},
                          {"deviceID": "D_008", "deviceName": "R2P4", "measureType": "DDD",
                                       "availableServices": ["MQTT", "REST"],
                                       "servicesDetails": [
                                           {"serviceType": "MQTT", "serviceIP": "ciao81",
                                            "topic": ["mio/prova8", "mio/prova88"]},
                                           {"serviceType": "REST", "serviceIP": "ciao82", "topic": []}
                                       ]}
                      ],
                      "product_type": "00"}
                     ]}


class WareBot:
    exposed = True

    def __init__(self, token):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
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
        # {
        #     'chatID':  ,
        #     'action':0 ----> Se l'utente rimuove
        #               1 ----> Se l'utente aggiunge
        #     'barcode':

        # }

        self.productRequestStatus = {}

    def on_chat_message(self, msg):
        self.bot.deleteMessage(telepot.message_identifier(msg))
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if 'text' in msg:
            message = msg['text']
        else:
            if content_type == 'photo':
                self.bot.download_file(
                    msg['photo'][-1]['file_id'], './file.png')

        if message.startswith('/'):
            if message == "/start":
                logged = False
                for status in self.sessionStatus:
                    if status['chatID'] == chat_ID:
                        if status['Log_in_status'] == 1:
                            logged = True
                            userID = status['userID']
                            isManager = userID.startswith('M_')
                            if isManager:
                                self.ManagerRoutine(userID, chat_ID, False)
                                break
                            else:
                                self.WorkerRoutine(userID, chat_ID, False)
                                break
                if not logged:
                    logged = False
                    self.startRoutine(chat_ID)

            else:
                self.bot.sendMessage(chat_ID, text="Command not supported")

        else:
            if message.startswith('U_') or message.startswith('M_'):
                # METTERE IL GET DEGLI UTENTI
                # GET catalog/users
                userIDs = []
                userDict = {'userList': [{"userID": "M_001"}, {
                    "userID": "U_002"}, {"userID": "U_003"}]}
                found = False
                registered = False
                # userDict=requests.get('http://127.0.0.1:8070/catalog/users')
                userList = userDict['userList']
                for user in userList:
                    userIDs.append(user['userID'])
                if message in userIDs:
                    found = True
                    for status in self.sessionStatus:
                        if status['chatID'] == chat_ID:
                            if status['isRegister']:
                                registered = True
                            else:
                                status['userID'] = message
                                status['isRegister'] = True
                                # body=json.dumps({'chatID':chat_ID})
                                # requests.post(url=f'http://127.0.0.1:8070/catalog/{message}/change_chatID',
                                #               data=body)

                if found and not registered:
                    found = False
                    text = f'Wonderful {message}, you signed-in succesfully, now click /start to see all functionalities of WareHouseBot'
                    self.bot.sendMessage(chat_ID, text=text)
                elif not found:
                    text = f'WRONG ID!!!\nPlease insert your userID to have access to all functionalities:'
                    self.bot.sendMessage(chat_ID, text=text)
            else:
                text = f'WRONG COMMAND!!!!'
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
            self.roomRoutine(chat_ID, userID)

        elif query_data == 'Overview_owner':
            pass
        elif query_data == 'Products_owner':
            pass
        elif query_data == 'Products_owner':
            pass
        elif query_data == 'Manage_product':
            pass
        elif query_data[0:2] == 'R_':
            for status in self.sessionStatus:
                if status['chatID'] == chat_ID:
                    userID = status['userID']
                    break
            self.deviceRoutine(chat_ID, userID, query_data)

        elif query_data[0:1] == 'D_':
            pass

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

    def roomRoutine(self, chat_ID, userID):
        roomDict = DICT
        assignedDict = {'roomIDs': ['R_001', 'R_002']}
        # roomDict=requests.get('http://127.0.0.1:8070/catalog/rooms')
        # assignedDict=requests.get(f'http://127.0.0.1:8070/catalog/{userID}/assigned_rooms')
        roomsList = roomDict['roomList']
        assignedRooms = assignedDict['roomIDs']
        inline = []
        buttons = []
        cnt = 0

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

    def deviceRoutine(self, chat_ID, userID, roomID):
        roomDict = DICT
        assignedDict = {'roomIDs': ['R_001', 'R_002']}
        # roomDict=requests.get('http://127.0.0.1:8070/catalog/rooms')
        # assignedDict=requests.get(f'http://127.0.0.1:8070/catalog/{userID}/assigned_rooms')
        roomsList = roomDict['roomList']
        assignedRooms = assignedDict['roomIDs']
        inline = []
        buttons = []
        cnt = 0
        for room in roomsList:
            if room['roomID'] == roomID:
                for device in room['devicesList']:
                    cnt = cnt + 1
                    ID_room = room['roomID']
                    ID_device = device['deviceID']
                    text = f'{ID_device}'
                    ID = f'{ID_device}+{ID_room}'
                    inline.append(
                        InlineKeyboardButton(
                            text=text, callback_data=ID))
                    if cnt == 4:
                        buttons.append(inline)
                        inline = []
                        cnt = 0
                if cnt < 4:
                    buttons.append(inline)
            break
        buttons.append([InlineKeyboardButton(text='BACK⏪', callback_data='Statistics')])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text='Choose a  device',
                             reply_markup=keyboard)


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    token = conf["telegramToken"]
    bot = WareBot(token)
    cherryConf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.config.update(
        {'server.socket_host': '0.0.0.0', 'server.socket_port': 80})
    cherrypy.tree.mount(bot, '/', cherryConf)
    cherrypy.engine.start()
    cherrypy.engine.block()
