from js import console
from functools import partial 
from js import TimeoutPromise
from js import jsfetch
from js import renderApp
from js import RequestAnimationFramePromise
import json
import math
import time

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
        self._response = None

    def __await__(self):
        _resp = yield self.promise
        return Response(_resp)

    async def __aenter__(self):
        return await self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def json(self):
        result = await self.text()
        return json.loads(result)

    async def text(self):
        if not self._response:
            await self
        result = await wrap_promise(self._response.text())
        return result

class Response:
    def __init__(self, resp):
        self._response = resp

    @property
    def ok(self):
        return self._response.ok
    
    @property
    def status(self):
        return int(self._response.status)

    @property
    def status_text(self):
        return self._response.statusText

    async def json(self):
        result = await self.text()
        return json.loads(result)

    async def text(self):
        result = await wrap_promise(self._response.text())
        return result
    async def read_chunks(self):
        stream_reader = self._response.body.getReader()

        while 1:
            chunk = await wrap_promise(stream_reader.read())
            if chunk['value'] is not None:
                yield chunk['value']
            if chunk['done']:
                return


class WrappedPromise:
    def __init__(self, promise):
        self.promise = promise
    def __await__(self):
        x = yield self.promise
        return x


def wrap_promise(promise):
    return WrappedPromise(promise)


class Fetcher:
    def __init__(self, base_url=""):
        self.base_url = base_url

    def get(self, path):
        promise = jsfetch(self.base_url+path)
        return Request(promise)

def sleep(time):
    return Waiter(time)

class PromiseException(RuntimeError):
    pass

class WebLoop:
    def __init__(self):
        self.coros = []
    def call_soon(self, coro):
        self.step(coro)
    def step(self, coro, arg=None):
        try:
            x = coro.send(arg)
            x = x.then(partial(self.step, coro))
            x.catch(partial(self.fail,coro))
        except StopIteration as result:
            pass

    def fail(self, coro,arg=None):
        try:
            coro.throw(PromiseException(arg))
        except StopIteration:
            pass
    
    def request_animation_frame(self):
        if not hasattr(self, "raf_event"):
            self.raf_event = RAFEvent()
        return self.raf_event

class RAFEvent:
    def __init__(self):
        self.awaiters = []
        self.promise = None
    def __await__(self):
        if self.promise is None:
            self.promise = RequestAnimationFramePromise()
        x = yield self.promise
        self.promise = None
        return x

class StateManager:
    """
        This class implements one way to handle global state.
        If one of the items is changed, the app and all its
        components are rendered, but only after waiting for
        an animation frame.
    """
    def __init__(self):
        self.state = dict()
        self._scheduled = False
        self.set_dirty()
    def set_dirty(self):
        self.dirty = True
        if self._scheduled:
            loop.call_soon(self.update())
            return
        self._scheduled = True

    async def update(self):
        await loop.request_animation_frame()
        renderApp(self.state)
        self.scheduled = False
        self.dirty = False

    def __setitem__(self, key, value):
        self.state[key] = value
        self.set_dirty()
    
    
async def task():
    print("task started")
    x = await sleep(1000)
    x = await task2()
    try:
        await task3()
    except RuntimeError as e:
        print("caught", repr(e))

    print("task finishing")

async def task2():
    print("enter task2")
    for i in range(5):
        await sleep(1000)
        state['status'] = f"Status {i}"
    for i in range(1000):
        x = await loop.request_animation_frame()
        state['status'] = f"Status {i}"
    return "(task2)"

async def task3():
    print("Throwing...")
    raise RuntimeError()

async def task4():
    d = dict(left=0,top=100, label="")
    start = time.time()
    while 1:
        t = time.time()
        await sleep(1)
        #await loop.request_animation_frame()
        state['box'] = d
        d['left'] = 300 + math.sin(t/20*2*math.pi)*300
        d['top'] = 100

async def fetching_task():
    print("Trying a fetch")
    base = Fetcher("http://localhost:8080")
    request = base.get("/packages.json")
    response = await request
    obj = await response.json()
    async with base.get("/packages.json") as response:
        print(response.status, response.status_text)
        print(len(await response.text()))

    async with base.get("/packages.json") as response:
        async for chunk in response.read_chunks():
            print("chunk:", chunk)

    async with base.get("/non_existing_file") as response:
        print(response.ok, response.status, response.status_text)
        text = await response.text()
    
    try:
        async with Fetcher("https://localhost:8080").get("/") as response:
            text = await response.text()
    except Exception as e:
        print("caught:", e)
    
loop = WebLoop()
state = StateManager()
state["status"] = "First Status!"
loop.call_soon(task())
loop.call_soon(task4())
loop.call_soon(fetching_task())