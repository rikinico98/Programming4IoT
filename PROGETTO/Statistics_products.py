# Do some statistics on the products and return them to the Telegram bot.

import cherrypy
import json
import requests

#####################################################################################################################################
# impostare la richiesta REST in modo tale da avere

        # GET
        # db/all                                            # retrieve all sold and stored products
        # db/sold/all                                       # retrieve all sold products
        # db/stored/all                                     # retrieve all stored products
        # db/stored/ID_stanza/all                           # retrieve all the products stored in ID_stanza
        # db/stored/ID_stanza/ID_prodotto/all               # retrieve the product ID_prodotto from the room ID_stanza
        # db/stored/threshold/all?th=num                    # retrieve all products whose quantity is smaller than num
        # db/stored/ID_stanza/threshold/all?th=num          # retrieve all products whose quantity is smaller than num in ID_stanza
        # db/sold/most/all                                  # retrieve the best-selling product
        # db/sold/least/all                                 # recover the least sold product
        # db/sold/ID_stanza/most/all                        # retrieve the best-selling product in room ID_stanza
        # db/sold/ID_stanza/least/all                       # recover the least sold product in ID_stanza
        # db/sold/most/month/all?month=num_month            # retrieve the best-selling product in month "month"
        # db/sold/least/month/all?month=num_month           # recover the least sold product in month "month"
        # db/sold/ID_stanza/most/month/all?month=num_month  # retrieve the best-selling product in month "month" in ID_stanza
        # db/sold/ID_stanza/least/month/all?month=num_month # recover the least sold product in month "month" in ID_stanza
        # db/sold/most/year/all?year=num_year               # retrieve the best-selling product in year "year"
        # db/sold/least/year/all?year=num_year              # recover the least sold product in year "year"
        # db/sold/ID_stanza/most/year/all?year=num_year     # retrieve the best-selling product in year "year" in ID_stanza
        # db/sold/ID_stanza/least/year/all?year=num_year    # recover the least sold product in year "year" in ID_stanza
        # db/statistics/count/all                           # return the total number of products in the warehouse
        # db/statistics/count/ID_stanza/all                 # return the total number of products in ID_stanza
        # db/statistics/mean/all                            # return the mean value of the products sold
        # db/statistics/total/all                           # return the total value of the products sold
        # db/statistics/mode/all                            # return the products that are more present in the warehouse
        # db/statistics/mode/ID_stanza/all                  # return the products that are more present in ID_stanza

#####################################################################################################################################

class StatisticsProducts():
    exposed = True

    def __init__(self):
        pass

    def GET(self, *uri, **params):
        uri = list(uri)
        server = uri[1]
        if uri[0] != "db":
            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
        if params == {}:
            if server == "all":
                # db/all
                r_devices_sold = requests.get(f'http://127.0.0.1:8090/db/all')
                r_devices_stored = requests.get(f'http://127.0.0.1:8080/db/all')
                if r_devices_sold.status_code == 200 and r_devices_stored.status_code == 200:
                    j_devices_sold = json.dumps(r_devices_sold.json(),indent=4)
                    d_devices_sold = json.loads(j_devices_sold)
                    j_devices_stored = json.dumps(r_devices_stored.json(),indent=4)
                    d_devices_stored = json.loads(j_devices_stored)
                    return json.dumps({"devices_sold": d_devices_sold, "devices_stored": d_devices_stored})
                else:
                    return json.dumps({"devices": "Something went wrong :C"})
            elif server == "sold":
                if len(uri) == 3:
                    if uri[2] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/sold/all
                        r_devices = requests.get(f'http://127.0.0.1:8090/db/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            return json.dumps(d_devices)
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                elif len(uri) > 3:
                    if uri[2] == "most":
                        if uri[3] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            # db/sold/most/all
                            r_devices = requests.get(f'http://127.0.0.1:8090/db/most/all')
                            if r_devices.status_code == 200:
                                j_devices = json.dumps(r_devices.json(),indent=4)
                                d_devices = {"devices": json.loads(j_devices)}
                                return json.dumps(d_devices)
                            else:
                                return json.dumps({"devices": "Something went wrong :C"})
                    elif uri[2] == "least":
                        if uri[3] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            # db/sold/least/all
                            r_devices = requests.get(f'http://127.0.0.1:8090/db/least/all')
                            if r_devices.status_code == 200:
                                j_devices = json.dumps(r_devices.json(),indent=4)
                                d_devices = {"devices": json.loads(j_devices)}
                                return json.dumps(d_devices)
                            else:
                                return json.dumps({"devices": "Something went wrong :C"})
                    else:
                        room_ID = uri[2]
                        if uri[3] == "most":
                            if uri[4] != "all":
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                            else:
                                # db/sold/ID_stanza/most/all
                                r_devices = requests.get(f'http://127.0.0.1:8090/db/{room_ID}/most/all')
                                if r_devices.status_code == 200:
                                    j_devices = json.dumps(r_devices.json(),indent=4)
                                    d_devices = {"devices": json.loads(j_devices)}
                                    return json.dumps(d_devices)
                                else:
                                    return json.dumps({"devices": "Something went wrong :C"})
                        elif uri[3] == "least":
                            if uri[4] != "all":
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                            else:
                                # db/sold/ID_stanza/least/all
                                r_devices = requests.get(f'http://127.0.0.1:8090/db/{room_ID}/least/all')
                                if r_devices.status_code == 200:
                                    j_devices = json.dumps(r_devices.json(),indent=4)
                                    d_devices = {"devices": json.loads(j_devices)}
                                    return json.dumps(d_devices)
                                else:
                                    return json.dumps({"devices": "Something went wrong :C"})
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            elif server == "stored":
                if len(uri) == 3:
                    if uri[2] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/stored/all
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            return json.dumps(d_devices)
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                elif len(uri) > 3:
                    room_ID = uri[2]
                    if uri[3] == "all":
                        # db/stored/ID_stanza/all
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/{room_ID}/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            return json.dumps(d_devices)
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    elif uri[4] == "all":
                        # db/stored/ID_stanza/ID_prodotto/all
                        product_ID = uri[3]
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/{room_ID}/{product_ID}/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            return json.dumps(d_devices)
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            elif server == "statistics":
                statistics = uri[2]
                if statistics == "count":
                    if uri[3] == "all":
                        # db/statistics/count/all
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            counter = 0
                            for item in d_devices["devices"]:
                                counter += 1
                            return json.dumps({"count": counter})
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    elif uri[4] == "all":
                        # db/statistics/count/ID_stanza/all
                        room_ID = uri[3]
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/{room_ID}/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            counter = 0
                            for item in d_devices["devices"]:
                                counter += 1
                            return json.dumps({"count": counter})
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif statistics == "mean":
                    if uri[3] == "all":
                        # db/statistics/mean/all 
                        r_devices = requests.get(f'http://127.0.0.1:8090/db/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            counter = 0
                            accumulator = 0
                            for item in d_devices["devices"]:
                                counter += 1
                                accumulator += item["quantity"]
                            return json.dumps({"mean": accumulator/counter})
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif statistics == "total":
                    if uri[3] == "all":
                        # db/statistics/total/all 
                        r_devices = requests.get(f'http://127.0.0.1:8090/db/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            accumulator = 0
                            for item in d_devices["devices"]:
                                accumulator += item["quantity"]
                            return json.dumps({"total": accumulator})
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif statistics == "mode":
                    if uri[3] == "all":
                        # db/statistics/mode/all
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            quantity = 0
                            for item in d_devices["devices"]:
                                if item["quantity"] > quantity:
                                    quantity = item["quantity"]
                            list_items = []
                            for item in d_devices["devices"]:
                                if item["quantity"] == quantity:
                                    list_items.append(item)
                            return json.dumps({"mode": list_items})
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                    elif uri[4] == "all":
                        # db/statistics/mode/ID_stanza/all
                        room_ID = uri[3]
                        room_ID = uri[3]
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/{room_ID}/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            quantity = 0
                            for item in d_devices["devices"]:
                                if item["quantity"] > quantity:
                                    quantity = item["quantity"]
                            list_items = []
                            for item in d_devices["devices"]:
                                if item["quantity"] == quantity:
                                    list_items.append(item)
                            return json.dumps({"mode": list_items})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            else:
                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
        else:
            if server == "sold":
                if uri[2] == "most":
                    if uri[4] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        if uri[3] == "month":
                            # db/sold/most/month/all?month=num_month
                            month = params["month"]
                            r_devices = requests.get(f'http://127.0.0.1:8090/db/most/{month}/all')
                            if r_devices.status_code == 200:
                                j_devices = json.dumps(r_devices.json(),indent=4)
                                d_devices = {"devices": json.loads(j_devices)}
                                return json.dumps(d_devices)
                            else:
                                return json.dumps({"devices": "Something went wrong :C"})
                        elif uri[3] == "year":
                            # db/sold/most/year/all?year=num_year
                            year = params["year"]
                            r_devices = requests.get(f'http://127.0.0.1:8090/db/most/{year}/all')
                            if r_devices.status_code == 200:
                                j_devices = json.dumps(r_devices.json(),indent=4)
                                d_devices = {"devices": json.loads(j_devices)}
                                return json.dumps(d_devices)
                            else:
                                return json.dumps({"devices": "Something went wrong :C"})
                        else:
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif uri[2] == "least":
                    if uri[4] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        if uri[3] == "month":
                            # db/sold/least/month/all?month=num_month
                            month = params["month"]
                            r_devices = requests.get(f'http://127.0.0.1:8090/db/least/{month}/all')
                            if r_devices.status_code == 200:
                                j_devices = json.dumps(r_devices.json(),indent=4)
                                d_devices = {"devices": json.loads(j_devices)}
                                return json.dumps(d_devices)
                            else:
                                return json.dumps({"devices": "Something went wrong :C"})
                        elif uri[3] == "year":
                            # db/sold/least/year/all?year=num_year
                            year = params["year"]
                            r_devices = requests.get(f'http://127.0.0.1:8090/db/least/{year}/all')
                            if r_devices.status_code == 200:
                                j_devices = json.dumps(r_devices.json(),indent=4)
                                d_devices = {"devices": json.loads(j_devices)}
                                return json.dumps(d_devices)
                            else:
                                return json.dumps({"devices": "Something went wrong :C"})
                        else:
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    room_ID = uri[2]
                    if uri[3] == "most":
                        if uri[5] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            if uri[4] == "month":
                                # db/sold/ID_stanza/most/month/all?month=num_month
                                month = params["month"]
                                r_devices = requests.get(f'http://127.0.0.1:8090/db/{room_ID}/most/{month}/all')
                                if r_devices.status_code == 200:
                                    j_devices = json.dumps(r_devices.json(),indent=4)
                                    d_devices = {"devices": json.loads(j_devices)}
                                    return json.dumps(d_devices)
                                else:
                                    return json.dumps({"devices": "Something went wrong :C"})
                            elif uri[4] == "year":
                                # db/sold/ID_stanza/most/year/all?year=num_year
                                year = params["year"]
                                r_devices = requests.get(f'http://127.0.0.1:8090/db/{room_ID}/most/{year}/all')
                                if r_devices.status_code == 200:
                                    j_devices = json.dumps(r_devices.json(),indent=4)
                                    d_devices = {"devices": json.loads(j_devices)}
                                    return json.dumps(d_devices)
                                else:
                                    return json.dumps({"devices": "Something went wrong :C"})
                            else:
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    elif uri[3] == "least":
                        if uri[5] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            if uri[4] == "month":
                                # db/sold/ID_stanza/least/month/all?month=num_month
                                month = params["month"]
                                r_devices = requests.get(f'http://127.0.0.1:8090/db/{room_ID}/least/{month}/all')
                                if r_devices.status_code == 200:
                                    j_devices = json.dumps(r_devices.json(),indent=4)
                                    d_devices = {"devices": json.loads(j_devices)}
                                    return json.dumps(d_devices)
                                else:
                                    return json.dumps({"devices": "Something went wrong :C"})
                            elif uri[4] == "year":
                                # db/sold/ID_stanza/least/year/all?year=num_year
                                year = params["year"]
                                r_devices = requests.get(f'http://127.0.0.1:8090/db/{room_ID}/least/{year}/all')
                                if r_devices.status_code == 200:
                                    j_devices = json.dumps(r_devices.json(),indent=4)
                                    d_devices = {"devices": json.loads(j_devices)}
                                    return json.dumps(d_devices)
                                else:
                                    return json.dumps({"devices": "Something went wrong :C"})
                            else:
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            elif server == "stored":
                if uri[2] == "threshold":
                    if uri[3] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/stored/threshold/all?th=num
                        num = params["th"]
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/quantity/{num}/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            return json.dumps(d_devices)
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                elif uri[3] == "threshold":
                    if uri[4] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/stored/ID_stanza/threshold/all?th=num
                        room_ID = uri[2]
                        num = params["th"]
                        r_devices = requests.get(f'http://127.0.0.1:8080/db/{room_ID}/quantity/{num}/all')
                        if r_devices.status_code == 200:
                            j_devices = json.dumps(r_devices.json(),indent=4)
                            d_devices = {"devices": json.loads(j_devices)}
                            return json.dumps(d_devices)
                        else:
                            return json.dumps({"devices": "Something went wrong :C"})
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            else:
                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.config.update({'server.socket_port': 8060})
    cherrypy.quickstart(StatisticsProducts(), '/', conf)