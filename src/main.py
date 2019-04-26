from js import console
from functools import partial 
from js import TimeoutPromise
from js import jsfetch
import json


class Waiter:
    def __init__(self, time):
        self.time = time
    def __await__(self):
        promise = TimeoutPromise(self.time)
        yield promise
        return self.time

class Request:
    def __init__(self, promise):
        self.promise = promise

    def __await__(self):
        _resp = yield self.promise
        return Response(_resp)

class WrappedPromise:
    def __init__(self, promise):
        self.promise = promise
    def __await__(self):
        x = yield self.promise
        return x

def wrap_promise(promise):
    return WrappedPromise(promise)

class Response:
    def __init__(self, resp):
        self._response = resp
        self.ok = resp.ok
        self.status = resp.status
        self.status_text = resp.statusText

    async def json(self):
        result = await self.text()
        return json.loads(result)

    async def text(self):
        result = await wrap_promise(self._response.text())
        return result

class Fetcher:
    def __init__(self, base_url=""):
        self.base_url = base_url

    def get(self, path):
        promise = jsfetch(self.base_url+path)
        return Request(promise)

def sleep(time):
    return Waiter(time)


class WebLoop:
    def __init__(self):
        self.coros = []
    def call_soon(self, coro):
        self.step(coro)
    def step(self, coro, arg=None):
        try:
            print("####stepping")
            x = coro.send(arg)
            x.then(partial(self.step, coro))
        except StopIteration as result:
            pass

async def task():
    print("task started")
    x = await sleep(1000)
    print("from await->",x)
    x = await task2()
    print("from await task2->",x)
    try:
        await task3()
    except RuntimeError as e:
        print("caught", repr(e))

    print("task finishing")

async def task2():
    print("enter task2")
    for i in range(5):
        print(i)
        await sleep(2000)
    return "(task2)"

async def task3():
    print("Throwing...")
    raise RuntimeError()

async def fetching_task():
    print("Trying a fetch")
    request = Fetcher("http://localhost:8080").get("/packages.json")
    result = await request
    obj = await result.json()
    print(len(obj["import_name_to_package_name"]))
loop = WebLoop()
loop.call_soon(task())
loop.call_soon(fetching_task())

