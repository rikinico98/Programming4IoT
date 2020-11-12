import json
import cherrypy
import requests


class BikeAnalyzer():
	exposed = True

	def __init__(self):
		pass

	def GET(self, *uri):
		r = requests.get('https://www.bicing.barcelona/en/get-stations')
		resources = r.json()
		cmd = uri[0]
		if cmd == 'slots' or cmd=='bikes':
			if len(uri)>1 and len(uri)<4:
				N = uri[1]
				order = uri[2]
			elif len(uri)>4:
				raise cherrypy.HTTPError(405, "Too many argument")
			else:
				N = '10'
				order = '1'
			if (N.isdigit() and (order == '0' or order == '1')):
				stations = resources['stations']
				if (order == '1'):
					sorted_stations = sorted(stations, key=lambda k: k[cmd], reverse=True)
					selected_stations = sorted_stations[0:int(N)]
					return json.dumps(selected_stations,indent=4)
				else:
					sorted_stations = sorted(stations, key=lambda k: k[cmd], reverse=False)
					selected_stations = sorted_stations[0:int(N)]
					return json.dumps(selected_stations,indent=4)
			else:
				raise cherrypy.HTTPError(406, "Wrong parameter")
		elif cmd == 'ebikes':
			if len(uri)>1 and len(uri)<4:
				N = uri[1]
				M = uri[2]
			elif len(uri)>4:
				raise cherrypy.HTTPError(405, "Too many argument")
			else:
				N = '10'
				M = '5'
			if (N.isdigit() and M.isdigit()):
				stations = resources['stations']
				ok_station = [];
				for station in stations:
					n_ebike=station.get('electrical_bikes')
					n_slots=station.get('slots')
					if n_ebike>int(N) and n_slots>int(M):
						ok_station.append(station)
				if len(ok_station) == 0:
					raise cherrypy.HTTPError(403, "No output for this input")
				else:
					return json.dumps(ok_station,indent=4)

		elif cmd=='count':
			if len(uri)>1:
				raise cherrypy.HTTPError(405, "Too many argument")
			stations = resources['stations']
			tot_slots=0
			tot_bikes=0
			for station in stations:
				n_bikes = station.get('bikes')
				n_slots = station.get('slots')
				tot_slots=tot_slots+int(n_slots)
				tot_bikes=tot_bikes+int(n_bikes)
			count_of_value=dict(num_slots=tot_slots,num_bikes=tot_bikes)
			return json.dumps(count_of_value,indent=4)




		else:
			raise cherrypy.HTTPError(404, "Wrong command")



if __name__=="__main__":



	# Standard configuration to serve the url "localhost:8080"
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tool.session.on': True
		}
	}
	cherrypy.config.update({'server.socket_port': 8080})
	cherrypy.quickstart(BikeAnalyzer(), '/', conf)
	cherrypy.engine.start()
	cherrypy.engine.block()