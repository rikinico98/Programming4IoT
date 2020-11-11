import SensorManager as sm
import json
import cherrypy


class SensorServer():
    exposed = True
    def __init__(self,filename):
        self.filename=filename
        self.contents=json.dumps(json.load(open(self.filename)))


    def GET(self,*uri):
        SM = sm.SensorManager(self.filename,self.contents)
        cond1 = (len(uri) != 0)
        if cond1:
            cmd=uri[0]
            if(len(uri)>1):
                variable = uri[1]
                if cmd == 'search_name':
                    found_devices=SM.searchByName(variable)
                    if len(found_devices)==0:
                        raise cherrypy.HTTPError(405, "Device absent")
                    Json_out = json.dumps(found_devices)
                    return Json_out

                elif cmd == 'search_ID':
                    found_devices = SM.searchByID(variable)
                    if found_devices== None:
                        raise cherrypy.HTTPError(405, "Device absent")
                    Json_out = json.dumps(found_devices)
                    return Json_out
                elif cmd == 'search_meas_type':
                    found_devices = SM.searchByMeasureType(variable)
                    if len(found_devices)==0:
                        raise cherrypy.HTTPError(405, "Device absent")
                    Json_out = json.dumps(found_devices)
                    return Json_out
                else:
                    raise cherrypy.HTTPError(404, "Wrong Command")
            else:
                if cmd == 'print_all':
                    return self.contents
                else:
                    raise cherrypy.HTTPError(404, "Wrong Command")
    def PUT(self):
        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        SM = sm.SensorManager(self.filename, self.contents)
        SM.insertDevice(jsonBody)
        self.contents=json.dumps(SM.td)
        return self.contents




if __name__=="__main__":



	# Standard configuration to serve the url "localhost:8080"
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tool.session.on': True
		}
	}
	cherrypy.config.update({'server.socket_port': 8080})
	cherrypy.quickstart(SensorServer('catalog.json'), '/', conf)
	cherrypy.engine.start()
	cherrypy.engine.block()


