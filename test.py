import restAPY
import json

def foo(request):
    if request["Type"] == "GET":
        return request
    elif request["Type"] == "POST":
        return json.loads(request["JSON"])



api = restAPY.API(8001, "0.0.0.0")
api.useTLS = False
api.setPath("/foo", foo)
api.useTLS = False
api.httpsPort = 8443
api.certchain = "/etc/letsencrypt/live/salkin.duckdns.org/fullchain.pem"
api.privkey = "/etc/letsencrypt/live/salkin.duckdns.org/privkey.pem"
api.redirectHttp = False
api.run()
