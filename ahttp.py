#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
作者：李C
邮箱：cszy2013@163.com
'''

from functools import partial
import asyncio
try:
	import aiohttp
except ImportError:
    raise RuntimeError('您没有安装aiohttp，请执行安装命令 pip install aiohttp  ')

__all__ = (
    'map',  'Session',
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'session', 'request'
)

status = [None, None, None]
result = []

class AsyncRequests():
	def __init__(self, method, url, **kwargs):
		self.method = method
		self.session = False
		self.url = url
		self.kwargs = kwargs

class GlobalSessionAsyncRequests():
	def __init__(self, method, url, **kwargs):
		self.method = method
		self.session= True
		self.url = url
		callback = kwargs.pop('callback', None)
		self.callback = callback
		self.kwargs = kwargs

class WithSession():
	def __init__(self):
		self.get = partial(GlobalSessionAsyncRequests, 'GET')
		self.options = partial(GlobalSessionAsyncRequests, 'OPTIONS')
		self.head = partial(GlobalSessionAsyncRequests, 'HEAD')
		self.post = partial(GlobalSessionAsyncRequests, 'POST')
		self.put = partial(GlobalSessionAsyncRequests, 'PUT')
		self.patch = partial(GlobalSessionAsyncRequests, 'PATCH')
		self.delete = partial(GlobalSessionAsyncRequests, 'DELETE')
	
get = partial(AsyncRequests, 'GET')
options = partial(AsyncRequests, 'OPTIONS')
head = partial(AsyncRequests, 'HEAD')
post = partial(AsyncRequests, 'POST')
put = partial(AsyncRequests, 'PUT')
patch = partial(AsyncRequests, 'PATCH')
delete = partial(AsyncRequests, 'DELETE')

def Session(cookies = None, headers = None, unsafe = False):
	status = [cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None ]
	return WithSession()
	
def map(tasks=[], pool=2, exception_handle = None):
	del result[:]
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future( run(tasks, pool, exception_handle) )
	loop.run_until_complete(future)
	#loop.close()
	return result

class Ahttp():
	def __init__(self,content,clientResponse):
		self.content = content
		self.clientResponse = clientResponse
		
	def raw(self):
		return self.clientResponse
		
	@property
	def url(self):
		return self.clientResponse.url
		
	@property
	def cookies(self):
		return self.clientResponse.cookies
		
	@property
	def headers(self):
		return self.clientResponse.headers

	@property
	def status(self):
		return self.clientResponse.status
	
	def text(self, encoding = 'utf-8'):
		return self.content.decode(encoding)

	def __repr__(self):
		return "<ahttp [{}]>".format(self.clientResponse.status)

	__str__=__repr__

async def run(tasks, pool, exception_handle):

    sem = asyncio.Semaphore(pool)
    all_tasks=[]
    async with aiohttp.ClientSession( cookies = status[0] , headers = status[1], cookie_jar = status[2] ) as session:
        for i in tasks:
            if i.session:
                task = asyncio.ensure_future( bound_fetch(sem, i , exception_handle, session=session) )
            else:
                task = asyncio.ensure_future( bound_fetch(sem, i, exception_handle) )
            all_tasks.append(task)
        await asyncio.wait(all_tasks)
		
async def fetch(session, i, exception_handle):
	try:
		if session:
			async with session.request(i.method, i.url, **(i.kwargs)) as resp:
				content = await resp.read()
				myAhttp = Ahttp(content,resp)
				result.append(myAhttp)
		else:
			async with aiohttp.request(i.method, i.url, **(i.kwargs)) as resp:
				content = await resp.read()
				myAhttp = Ahttp(content,resp)
				result.append(myAhttp)

		if i.callback:
			try:
				i.callback(myAhttp)
			except:
				pass
	except:
		#错误处理，如果出错，默认将当前任务作为参数传到指定的错误处理函数中
		result.append(None)
				
async def bound_fetch(sem, i, exception_handle, session = False ):
    # 限制信号量
    async with sem:
        await fetch(session, i, exception_handle)