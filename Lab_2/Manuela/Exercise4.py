import  json
import cherrypy
import os

class SensorRegister():
	exposed = True

	def __init__(self):
		self.device_list=[]
		self.jsonOut={}
		# self.id="tableBody"


	def GET(self):
		return open("index.html")

	def POST(self):
		dict_total = {}
		body = cherrypy.request.body.read()
		jsonBody = json.loads(body)
		self.device_list.append(jsonBody)
		dict_total = dict(devicesList=self.device_list)
		json.dump(dict_total, open('devices.json', 'w', ), indent=4)
		self.jsonOut = json.dumps(dict_total)
		return self.jsonOut


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
	cherrypy.tree.mount(SensorRegister(),'/',conf)
	cherrypy.config.update({'server.socket_port': 8089})
	cherrypy.engine.start()
	cherrypy.engine.block()