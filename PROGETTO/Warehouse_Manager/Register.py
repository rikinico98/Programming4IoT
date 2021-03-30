import cherrypy
import json
import os
import requests

class OpenWebService():
	exposed = True
	# l'url del catalog è noto a priori, unica cosa nota
	def __init__(self):
		self.url_catalog = "http://127.0.0.1:8070"
		self.url_create_channel_thingspeak = "https://api.thingspeak.com/channels.json"
		self.url_delete_channel_thingspeak = "https://api.thingspeak.com/channels" #+ channelID alla fine
		self.api_key = "LL8A82J0EWRBDUSQ" #questo è l'api key di Caterina per creare massimo 4 canali

	def GET(self, **params):
		return open("prova3_tabs.html")

	def POST(self):
		# qui bisogna inserire gli if che permettono di controllare 
		# di che tipo di body si tratta, se riguarda un device, un user o una stanza
		# nel caso di una nuova stanza bisogna creare il channel thingspeak		
		my_string = cherrypy.request.body.read()
		new_device = json.loads(my_string) #dictionary
		print(json.dumps(new_device, indent = 4))
		# per inserire un dispositivo sul catalog
		if new_device["command"] == "insert_device":
			body = new_device["body"]
			room = body["roomID"]
			del body["roomID"]
			r = requests.post(self.url_catalog + f'/catalog/{room}/{body["deviceID"]}/new', data=json.dumps(body, indent=4))
			return json.dumps(new_device, indent = 4)

		#  per inserire una stanza sul catalog
		# ogni volta che si inserisce una stanza si deve creare un canale thingspeak
		# e salvare channel ID, api_key_read e api_key_write
		if new_device["command"] == "insert_room":
			body = new_device["body"]
			# seguenti righe per creare il canale ThingSpeak
			#api_key=self.api_key&name=body["roonID"]
			#body_new_channel = {"apy_key": self.api_key, "name": body["roomID"]}
			print(self.url_create_channel_thingspeak + f'?api_key={self.api_key}&name={body["roomID"]}')
			response = requests.post(self.url_create_channel_thingspeak + f'?api_key={self.api_key}&name={body["roomID"]}&field1=Temperature&field2=Humidity&field3=Smoke&field4=Empty&field5=Empty&field6=Empty&field7=Empty&field8=Empty')
			diz1 = json.dumps(response.json(), indent = 4)
			diz = json.loads(diz1)#la risposta diventa dizionario
			#mi prendo le specifiche del canale e le salvo
			body["ThingSpeak"]["channelID"] = diz["id"]
			body["ThingSpeak"]["api_key_read"] = diz["api_keys"][0]["api_key"]
			body["ThingSpeak"]["api_key_write"] = diz["api_keys"][1]["api_key"]
			print(json.dumps(body, indent = 4))
			r = requests.post(self.url_catalog + f'/catalog/{body["roomID"]}/new', data=json.dumps(body, indent=4))
			return json.dumps(new_device, indent = 4)

		#per inserire un nuovo utente nel Catalog
		if new_device["command"] == "insert_user":
			body = new_device["body"]
			print(json.dumps(body, indent = 4))
			r = requests.post(self.url_catalog + f'/catalog/{body["userID"]}/new', data=json.dumps(body, indent=4))
			return json.dumps(new_device, indent = 4)

	def PUT(self, **params):
		# il put mi gestisce tutte le modifiche
		my_string = cherrypy.request.body.read()
		to_update = json.loads(my_string) #dictionary
		print(to_update)

		#ROOM'S updates
		if to_update["command"] == "update_api_key_read":
			body = to_update["body"]
			roomID = body["roomID"]
			del body["roomID"]
			#print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/TS_get', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)		
		elif to_update["command"] == "update_api_key_write":
			body = to_update["body"]
			roomID = body["roomID"]
			del body["roomID"]
			#print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/TS_post', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)			
		elif to_update["command"] == "update_channel_id":
			body = to_update["body"]
			roomID = body["roomID"]
			del body["roomID"]
			#print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/TS_channel', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)			
		elif to_update["command"] == "update_product_type":
			body = to_update["body"]
			roomID = body["roomID"]
			del body["roomID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/change_product_type', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "change_ranges":
			body = to_update["body"]
			roomID = body["roomID"]
			del body["roomID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/change_ranges', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		# DEVICES PUT	
		elif  to_update["command"]== "update_name":
			body = to_update["body"]
			roomID = body["roomID"]
			deviceID = body["deviceID"]
			del body["roomID"]
			del body["deviceID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/{deviceID}/update_name', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "change_meas_type":
			body = to_update["body"]
			roomID = body["roomID"]
			deviceID = body["deviceID"]
			del body["roomID"]
			del body["deviceID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/{deviceID}/change_meas_type', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "add_service_details":
			body = to_update["body"]
			roomID = body["roomID"]
			deviceID = body["deviceID"]
			del body["roomID"]
			del body["deviceID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/{deviceID}/add_service_details', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "change_topic":
			body = to_update["body"]
			roomID = body["roomID"]
			deviceID = body["deviceID"]
			del body["roomID"]
			del body["deviceID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/{deviceID}/change_topic', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "change_field":
			body = to_update["body"]
			roomID = body["roomID"]
			deviceID = body["deviceID"]
			del body["roomID"]
			del body["deviceID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{roomID}/{deviceID}/change_field', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		# USER PUT
		elif to_update["command"]== "add_assigned_rooms":
			body = to_update["body"]
			userID = body["userID"]
			del body["userID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{userID}/add_assigned_rooms', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "delete_assigned_rooms":
			body = to_update["body"]
			userID = body["userID"]
			del body["userID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{userID}/delete_assigned_rooms', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "change_role":
			body = to_update["body"]
			userID = body["olduserID"]
			del body["olduserID"]
			print(json.dumps(body, indent = 4))
			r = requests.put(self.url_catalog + f'/catalog/{userID}/change_role', data=json.dumps(body, indent=4))
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "delete_device":
			body = to_update["body"]
			roomID = body["roomID"]
			deviceID = body["deviceID"]
			r = requests.delete(self.url_catalog + f'/catalog/{roomID}/{deviceID}/delete')
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "delete_room":
			body = to_update["body"]
			roomID = body["roomID"]
			#mi serve il channel_id della stanza per eliminare il canale
			request_channel_id = requests.get(self.url_catalog + f'/catalog/{roomID}/TS_utilities')
			diz1 = json.dumps(request_channel_id.json(), indent = 4) #-> LA RICHIESTA DIVENTA JSON
			diz = json.loads(diz1) 
			channelID = diz["ThingSpeak"]["channelID"]
			r = requests.delete(self.url_catalog + f'/catalog/{roomID}/delete')
			#delete also thingspeak field
			response = requests.delete(self.url_delete_channel_thingspeak + f'/{channelID}' f'?api_key={self.api_key}')
			return json.dumps(to_update, indent = 4)
		elif to_update["command"]== "delete_user":
			body = to_update["body"]
			userID = body["userID"]
			r = requests.delete(self.url_catalog + f'/catalog/{userID}/delete')
			return json.dumps(to_update, indent = 4)
		else:
			pass


if __name__ == '__main__':
	conf={
		'/':{
				'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
				'tools.staticdir.root': os.path.abspath(os.getcwd()),
			},
		 '/css':{
		 'tools.staticdir.on': True,
		 'tools.staticdir.dir':'./css'
		 },
		 '/js':{
		 'tools.staticdir.on': True,
		 'tools.staticdir.dir':'./js'
		 },
	}		
	cherrypy.tree.mount(OpenWebService(),'/',conf)
	cherrypy.config.update({'server.socket_port': 8090})
	cherrypy.engine.start()
	cherrypy.engine.block()