from requests_html import HTML, HTMLSession
from aiohttp import ClientResponse
from functools import partial
from cchardet import detect
import json, aiohttp, asyncio, ctypes

__all__ = (
    'map',  'Session', 
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'session', 'request'
)

class Session():
    def __init__(self, *args, **kwargs):
        self.session = self
        self.headers = HTMLSession().headers
        self.cookies = {}
        self.request_pool = []

    def __getattr__(self, name):
        if name in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:
            new_req = AsyncRequestTask(headers=self.headers, session = self.session)
            new_req.__getattr__(name)
            self.request_pool.append(new_req)
            return new_req.get_params

    def __repr__(self):
        return f"<Ahttp Session [id:{id(self.session)} client]>"

class AsyncRequestTask():
    def __init__(self, *args, session=None, headers=None, **kwargs):
        self.session = session
        self.headers = headers
        self.cookies = None
        self.kw = kwargs
        self.method = None

    def __getattr__(self, name):
        if name in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:
            self.method = name
            return self.get_params

    def __repr__(self):
        return f"<AsyncRequestTask session:[{id(self.session)}] req:[{self.method.upper()}:{self.url}]>"

    def get_params(self, *args, **kw):
        self.url = args[0]
        self.args = args[1:]
        if "callback" in kw:
            self.callback = kw['callback']
            kw.pop("callback")
        else:
            self.callback = None
        if "headers" in kw:
            self.headers = kw['headers']
            kw.pop("headers")
        self.kw = kw
        return self
    
    def run(self):
        future = asyncio.ensure_future(single_req(self))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
        new_res = AhttpResponse(self.result, self.content, self)
        return [new_res, self.callback and self.callback(new_res)][0]

class AhttpResponse():
    def __init__(self, res, content, req, *args, **kwargs):
        self.content = content
        self.req = req
        self.raw = self.clientResponse = res

    @property
    def text(self):
        code_type = detect(self.content)
        return self.content.decode(code_type['encoding'])
    @property
    def url(self):
        return self.clientResponse.url
    @property
    def cookies(self):
        return self.clientResponse.cookies
        
    @property
    def headers(self):
        return self.clientResponse.headers

    def json(self):
        return json.loads(self.text)

    @property
    def status(self):
        return self.clientResponse.status
        
    @property
    def method(self):
        return self.clientResponse.method
    @property
    def html(self):
        return self.dom
    @property
    def dom(self):
        """
        返回一个requests_html对象，
        支持所有requests_html的html对象的操作。例如find, xpath, render（先安装chromium浏览器）
        """
        html = HTML(html=self.text)
        html.url = self.raw.url
        return html

    def __repr__(self):
        return f"<AhttpResponse status[{self.status}] url=[{self.url}]>"

def run(tasks, pool=2, max_try=3, callback=None, order=False):
    if not isinstance(tasks, list):
        raise "the tasks of run must be a list object"
    conn = aiohttp.TCPConnector(use_dns_cache=True, loop=asyncio.get_event_loop(), ssl=False)
    sem = asyncio.Semaphore(pool)
    result = []
    loop = asyncio.get_event_loop()
    loop.run_until_complete(multi_req(tasks, conn, sem, max_try, callback, result))
    if not order:
        return result
    rid = [*map(lambda x:id(x), tasks)]
    new_res = [*rid]
    for i in result:
        index = rid.index(id(i.req))
        rid[index] = 0
        new_res[index] = i
    return new_res
    
def wrap_headers(headers):
    new_headers = {}
    for k, v in headers.items():
        new_headers[k] = str(v)
    return new_headers

async def single_req(self):
    async with aiohttp.ClientSession(cookies=self.cookies) as session:
        async with session.request(self.method, self.url, *self.args, ssl=False, headers=wrap_headers(self.headers or self.session.headers), **self.kw) as resp:
            res = await resp.read()
            self.result, self.content = resp, res

async def multi_req(tasks, conn, sem, max_try, callback, result):
    sessions_list = {}
    new_tasks = []
    for i in tasks:
        if id(i.session) not in sessions_list:
            sessions_list[id(i.session)]=aiohttp.ClientSession(connector_owner=False, connector=conn, cookies=i.session.cookies)
        new_tasks.append(asyncio.ensure_future(control_sem(sem, i, sessions_list[id(i.session)], result)))

    await asyncio.wait(new_tasks)
    await asyncio.wait([asyncio.ensure_future(v.close()) for k,v in sessions_list.items()])
    await conn.close()#关闭tcp连接器

async def control_sem(sem, i, session, result):
    # 限制信号量
	async with sem:
		await fetch(i, session, result)

async def fetch(i, session, result):
    headers=wrap_headers(i.headers or ctypes.cast(i.session, ctypes.py_object).value.headers)
    async with session.request(i.method, i.url, *i.args, headers=headers, **i.kw) as resp:
        res = await resp.read()
        r = AhttpResponse(resp, res, i)
        result.append(r)
        if i.callback:
            i.callback(r)

def create_session(method, *args, **kw):
    sess = Session()
    return {"get" : sess.get, "post":sess.post, "options" : sess.options, "head":sess.head, "put":sess.put, "patch":sess.patch, "delete":sess.delete}[method](*args, **kw)

get = partial(create_session, "get")
post = partial(create_session, "post")
options = partial(create_session, "options")
head = partial(create_session, "head")
put = partial(create_session, "put")
patch = partial(create_session, "patch")
delete = partial(create_session, "delete")