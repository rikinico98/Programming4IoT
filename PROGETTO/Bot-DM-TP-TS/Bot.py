import telepot
from telepot.loop import MessageLoop

class MyBot:
    def __init__(self,token, mex):
    # Local token
        self.tokenBot=token
        self.mex = mex
        # Catalog token
        #self.tokenBot=requests.get()
        self.bot=telepot.Bot(self.tokenBot)
        #ricevi i messaggi e devi dire cosa fare quando ricevi 
        #un messaggio; on_chat_message is executed as a callback
        MessageLoop(self.bot,{'chat': self.on_chat_message}).run_as_thread()
        
    # il msg è un json
    def on_chat_message(self,msg):
        #chat_type dice se è una chat di gruppo
        content_type, chat_type ,chat_ID = telepot.glance(msg)
        message=msg['text'] #json format
        if message == '/statistiche':
            #invio il messaggio con le statistiche
            self.bot.sendMessage(chat_ID,text = self.mex)

