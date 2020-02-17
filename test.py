import restAPY

api = restAPY.API(8001, "0.0.0.0")
api.useTLS = False
api.run()
