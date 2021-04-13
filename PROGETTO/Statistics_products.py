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
        # db/statistics/mean/all                            # return the mean quantity of the products sold
        # db/statistics/total/all                           # return the total quantity of the products sold
        # db/statistics/mode/all                            # return the products that are more present in the warehouse
        # db/statistics/mode/ID_stanza/all                  # return the products that are more present in ID_stanza

#####################################################################################################################################

class StatisticsProducts():
    exposed = True

    def __init__(self):
        # Request URL to catalog
        r_url = requests.get(f'{URL}/catalog/URL')
        j_url = json.dumps(r_url.json(),indent=4)
        d_url = json.loads(j_url)
        self.url_sold = d_url["URL"]["soldProductsURL"]
        self.url_stored = d_url["URL"]["storedProductsURL"]

    def GET(self, *uri, **params):
        uri = list(uri)
        server = uri[1]
        if uri[0] != "db":
            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
        if params == {}:
            if server == "all":
                # db/all
                r_products_sold = requests.get(f'{self.url_sold}/db/all')
                r_products_stored = requests.get(f'{self.url_stored}/db/all')
                if r_products_sold.status_code == 200 and r_products_stored.status_code == 200:
                    j_products_sold = json.dumps(r_products_sold.json(),indent=4)
                    d_products_sold = json.loads(j_products_sold)
                    j_products_stored = json.dumps(r_products_stored.json(),indent=4)
                    d_products_stored = json.loads(j_products_stored)
                    return json.dumps({"products_sold": d_products_sold, "products_stored": d_products_stored})
                else:
                    return json.dumps({"products_sold": -1, "products_stored": -1})
            elif server == "sold":
                if len(uri) == 3:
                    if uri[2] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/sold/all
                        r_products = requests.get(f'{self.url_sold}/db/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            return json.dumps(d_products)
                        else:
                            return json.dumps({"products": -1})
                elif len(uri) > 3:
                    if uri[2] == "most":
                        if uri[3] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            # db/sold/most/all
                            r_products = requests.get(f'{self.url_sold}/db/most/all')
                            if r_products.status_code == 200:
                                j_products = json.dumps(r_products.json(),indent=4)
                                d_products = {"products": json.loads(j_products)}
                                return json.dumps(d_products)
                            else:
                                return json.dumps({"products": -1})
                    elif uri[2] == "least":
                        if uri[3] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            # db/sold/least/all
                            r_products = requests.get(f'{self.url_sold}/db/least/all')
                            if r_products.status_code == 200:
                                j_products = json.dumps(r_products.json(),indent=4)
                                d_products = {"products": json.loads(j_products)}
                                return json.dumps(d_products)
                            else:
                                return json.dumps({"products": -1})
                    else:
                        room_ID = uri[2]
                        if uri[3] == "most":
                            if uri[4] != "all":
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                            else:
                                # db/sold/ID_stanza/most/all
                                r_products = requests.get(f'{self.url_sold}/db/{room_ID}/most/all')
                                if r_products.status_code == 200:
                                    j_products = json.dumps(r_products.json(),indent=4)
                                    d_products = {"products": json.loads(j_products)}
                                    return json.dumps(d_products)
                                else:
                                    return json.dumps({"products": -1})
                        elif uri[3] == "least":
                            if uri[4] != "all":
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                            else:
                                # db/sold/ID_stanza/least/all
                                r_products = requests.get(f'{self.url_sold}/db/{room_ID}/least/all')
                                if r_products.status_code == 200:
                                    j_products = json.dumps(r_products.json(),indent=4)
                                    d_products = {"products": json.loads(j_products)}
                                    return json.dumps(d_products)
                                else:
                                    return json.dumps({"products": -1})
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            elif server == "stored":
                if len(uri) == 3:
                    if uri[2] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/stored/all
                        r_products = requests.get(f'{self.url_stored}/db/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            return json.dumps(d_products)
                        else:
                            return json.dumps({"products": -1})
                elif len(uri) > 3:
                    room_ID = uri[2]
                    if uri[3] == "all":
                        # db/stored/ID_stanza/all
                        r_products = requests.get(f'{self.url_stored}/db/{room_ID}/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            return json.dumps(d_products)
                        else:
                            return json.dumps({"products": -1})
                    elif uri[4] == "all":
                        # db/stored/ID_stanza/ID_prodotto/all
                        product_ID = uri[3]
                        r_products = requests.get(f'{self.url_stored}/db/{room_ID}/{product_ID}/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            return json.dumps(d_products)
                        else:
                            return json.dumps({"products": -1})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            elif server == "statistics":
                statistics = uri[2]
                if statistics == "count":
                    if uri[3] == "all":
                        # db/statistics/count/all
                        r_products = requests.get(f'{self.url_stored}/db/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            counter = 0
                            for item in d_products["products"]:
                                counter += 1
                            return json.dumps({"count": counter})
                        else:
                            return json.dumps({"count": -1})
                    elif uri[4] == "all":
                        # db/statistics/count/ID_stanza/all
                        room_ID = uri[3]
                        r_products = requests.get(f'{self.url_stored}/db/{room_ID}/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            counter = 0
                            for item in d_products["products"]:
                                counter += 1
                            return json.dumps({"count": counter})
                        else:
                            return json.dumps({"count": -1})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif statistics == "mean":
                    if uri[3] == "all":
                        # db/statistics/mean/all
                        r_products = requests.get(f'{self.url_sold}/db/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            counter = 0
                            accumulator = 0
                            for item in d_products["products"]:
                                counter += 1
                                accumulator += item["quantity"]
                            return json.dumps({"mean": accumulator/counter})
                        else:
                            return json.dumps({"mean": -1})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif statistics == "total":
                    if uri[3] == "all":
                        # db/statistics/total/all
                        r_products = requests.get(f'{self.url_sold}/db/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            accumulator = 0
                            for item in d_products["products"]:
                                accumulator += item["quantity"]
                            return json.dumps({"total": accumulator})
                        else:
                            return json.dumps({"total": -1})
                    else:
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif statistics == "mode":
                    if uri[3] == "all":
                        # db/statistics/mode/all
                        r_products = requests.get(f'{self.url_stored}/db/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            quantity = 0
                            for item in d_products["products"]:
                                if item["quantity"] > quantity:
                                    quantity = item["quantity"]
                            list_items = []
                            for item in d_products["products"]:
                                if item["quantity"] == quantity:
                                    list_items.append(item)
                            return json.dumps({"mode": list_items})
                        else:
                            return json.dumps({"mode": -1})
                    elif uri[4] == "all":
                        # db/statistics/mode/ID_stanza/all
                        room_ID = uri[3]
                        room_ID = uri[3]
                        r_products = requests.get(f'{self.url_stored}/db/{room_ID}/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            quantity = 0
                            for item in d_products["products"]:
                                if item["quantity"] > quantity:
                                    quantity = item["quantity"]
                            list_items = []
                            for item in d_products["products"]:
                                if item["quantity"] == quantity:
                                    list_items.append(item)
                            return json.dumps({"mode": list_items})
                        else:
                            return json.dumps({"mode": -1})
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
                            r_products = requests.get(f'{self.url_sold}/db/most/{month}/all')
                            if r_products.status_code == 200:
                                j_products = json.dumps(r_products.json(),indent=4)
                                d_products = {"products": json.loads(j_products)}
                                return json.dumps(d_products)
                            else:
                                return json.dumps({"products": -1})
                        elif uri[3] == "year":
                            # db/sold/most/year/all?year=num_year
                            year = params["year"]
                            r_products = requests.get(f'{self.url_sold}/db/most/{year}/all')
                            if r_products.status_code == 200:
                                j_products = json.dumps(r_products.json(),indent=4)
                                d_products = {"products": json.loads(j_products)}
                                return json.dumps(d_products)
                            else:
                                return json.dumps({"products": -1})
                        else:
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif uri[2] == "least":
                    if uri[4] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        if uri[3] == "month":
                            # db/sold/least/month/all?month=num_month
                            month = params["month"]
                            r_products = requests.get(f'{self.url_sold}/db/least/{month}/all')
                            if r_products.status_code == 200:
                                j_products = json.dumps(r_products.json(),indent=4)
                                d_products = {"products": json.loads(j_products)}
                                return json.dumps(d_products)
                            else:
                                return json.dumps({"products": -1})
                        elif uri[3] == "year":
                            # db/sold/least/year/all?year=num_year
                            year = params["year"]
                            r_products = requests.get(f'{self.url_sold}/db/least/{year}/all')
                            if r_products.status_code == 200:
                                j_products = json.dumps(r_products.json(),indent=4)
                                d_products = {"products": json.loads(j_products)}
                                return json.dumps(d_products)
                            else:
                                return json.dumps({"products": -1})
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
                                r_products = requests.get(f'{self.url_sold}/db/{room_ID}/most/{month}/all')
                                if r_products.status_code == 200:
                                    j_products = json.dumps(r_products.json(),indent=4)
                                    d_products = {"products": json.loads(j_products)}
                                    return json.dumps(d_products)
                                else:
                                    return json.dumps({"products": -1})
                            elif uri[4] == "year":
                                # db/sold/ID_stanza/most/year/all?year=num_year
                                year = params["year"]
                                r_products = requests.get(f'{self.url_sold}/db/{room_ID}/most/{year}/all')
                                if r_products.status_code == 200:
                                    j_products = json.dumps(r_products.json(),indent=4)
                                    d_products = {"products": json.loads(j_products)}
                                    return json.dumps(d_products)
                                else:
                                    return json.dumps({"products": -1})
                            else:
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    elif uri[3] == "least":
                        if uri[5] != "all":
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                        else:
                            if uri[4] == "month":
                                # db/sold/ID_stanza/least/month/all?month=num_month
                                month = params["month"]
                                r_products = requests.get(f'{self.url_sold}/db/{room_ID}/least/{month}/all')
                                if r_products.status_code == 200:
                                    j_products = json.dumps(r_products.json(),indent=4)
                                    d_products = {"products": json.loads(j_products)}
                                    return json.dumps(d_products)
                                else:
                                    return json.dumps({"products": -1})
                            elif uri[4] == "year":
                                # db/sold/ID_stanza/least/year/all?year=num_year
                                year = params["year"]
                                r_products = requests.get(f'{self.url_sold}/db/{room_ID}/least/{year}/all')
                                if r_products.status_code == 200:
                                    j_products = json.dumps(r_products.json(),indent=4)
                                    d_products = {"products": json.loads(j_products)}
                                    return json.dumps(d_products)
                                else:
                                    return json.dumps({"products": -1})
                            else:
                                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            elif server == "stored":
                if uri[2] == "threshold":
                    if uri[3] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/stored/threshold/all?th=num
                        num = params["th"]
                        r_products = requests.get(f'{self.url_stored}/db/quantity/{num}/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            return json.dumps(d_products)
                        else:
                            return json.dumps({"products": -1})
                elif uri[3] == "threshold":
                    if uri[4] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/stored/ID_stanza/threshold/all?th=num
                        room_ID = uri[2]
                        num = params["th"]
                        r_products = requests.get(f'{self.url_stored}/db/{room_ID}/quantity/{num}/all')
                        if r_products.status_code == 200:
                            j_products = json.dumps(r_products.json(),indent=4)
                            d_products = {"products": json.loads(j_products)}
                            return json.dumps(d_products)
                        else:
                            return json.dumps({"products": -1})
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            else:
                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")

if __name__ == "__main__":
    # Get catalog URL from settings file
    f = open('Settings.json',)
    data = json.load(f)
    URL = data["catalogURL"]
    # Request port to catalog
    r_port = requests.get(f'{URL}/catalog/service_comm_port')
    j_port = json.dumps(r_port.json(),indent=4)
    d_port = json.loads(j_port)
    port = d_port["service_comm_port"]["port_databaseStats"]
    # Define conf dict
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.tree.mount(StatisticsProducts(),'/',conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port':port})
    cherrypy.engine.start()
    cherrypy.engine.block()
