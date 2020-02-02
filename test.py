import restAPY

api = restAPY.API(8000)
#api.port = 8000
data = {
    1:"a",
    2:"b",
    3:"c",
    "...":"...",
    26:"z"
}

api.setPath("/", data)
api.setPath("/data", "data")

api.run()

#restAPY.run_api(8000)
