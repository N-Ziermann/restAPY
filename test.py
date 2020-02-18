import restAPY

def foo(request):
    return request



api = restAPY.API(8001, "0.0.0.0")
api.useTLS = False
api.setPath("/foo", foo)
api.run()
