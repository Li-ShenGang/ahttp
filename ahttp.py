#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
作者：李C
邮箱：cszy2013@163.com
'''

from functools import partial
from random import random
import asyncio, weakref
try:
	import aiohttp
except ImportError:
    raise RuntimeError('您没有安装aiohttp，请执行安装命令 pip install aiohttp  ')

__all__ = (
    'map',  'Session',
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'session', 'request'
)

result = []
all_tasks = []
sessiondict = {}

class AsyncRequests():
	def __init__(self, method, url, session=False, headers=None, cookies=None, unsafe=None, mark='1111111111', **kwargs):
		self.method, self.session, self.url, self.mark = method, session, url, mark
		callback = kwargs.pop('callback', None)
		self.callback = callback
		self.kwargs = kwargs
		if not session:
			self.sessiondict = (cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None)
	def run(self, pool=2, exception_handle = None):
		result = run([self], pool=pool, exception_handle=exception_handle)
		return result[0]

class WithSession():
	def __init__(self, mark, session=True):
		self.get = partial(AsyncRequests, 'GET', session=session, mark=mark)
		self.options = partial(AsyncRequests, 'OPTIONS', session=session, mark=mark)
		self.head = partial(AsyncRequests, 'HEAD', session=session, mark=mark)
		self.post = partial(AsyncRequests, 'POST', session=session, mark=mark)
		self.put = partial(AsyncRequests, 'PUT', session=session, mark=mark)
		self.patch = partial(AsyncRequests, 'PATCH', session=session, mark=mark)
		self.delete = partial(AsyncRequests, 'DELETE', session=session, mark=mark)
	
get = partial(AsyncRequests, 'GET')
options = partial(AsyncRequests, 'OPTIONS')
head = partial(AsyncRequests, 'HEAD')
post = partial(AsyncRequests, 'POST')
put = partial(AsyncRequests, 'PUT')
patch = partial(AsyncRequests, 'PATCH')
delete = partial(AsyncRequests, 'DELETE')

def Session(cookies = None, headers = None, unsafe = None):
	#status = [cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None ]
	mark = str(round(random()*10**10))
	sessiondict[mark] = (cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None)
	return WithSession(mark=mark)
	
def run(tasks, pool=2, exception_handle = None):
	del result[:]
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future( go(tasks, pool, exception_handle) )
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
		
	@property
	def method(self):
		return self.clientResponse.method
	
	def text(self, encoding = 'utf-8'):
		return self.content.decode(encoding)

	def __repr__(self):
		return "<ahttp [{}]>".format(self.clientResponse.status)

	__str__=__repr__

async def go(tasks, pool, exception_handle):
	del all_tasks[:]
	sem = asyncio.Semaphore(pool)
	classify={}
	[ classify[i.mark].append(i) if classify.get(i.mark, 0) else classify.setdefault(i.mark,[i]) for i in tasks ]
	
	try:
		for i in classify.pop('1111111111'):
			all_tasks.append( asyncio.ensure_future( control_sem(sem, i , exception_handle, session=False) ) )
	except:
		pass
	for i in classify:
		async with aiohttp.ClientSession( cookies = sessiondict[i][0] , headers = sessiondict[i][1], cookie_jar = sessiondict[i][2] ) as locals()['session{}'.format(i)]:
			for j in classify[i]:
				all_tasks.append( asyncio.ensure_future( control_sem(sem, j , exception_handle, session=locals()['session{}'.format(i)]) ) )
			await asyncio.wait( all_tasks )

async def fetch(session, i, exception_handle):
	try:
		if session:
			async with session.request(i.method, i.url, **(i.kwargs)) as resp:
				content = await resp.read()
				myAhttp = Ahttp(content,resp)
				result.append(myAhttp)
		else:
			async with aiohttp.ClientSession( cookies = i.sessiondict[0] , headers = i.sessiondict[1], cookie_jar = i.sessiondict[2] ) as session2:
				async with session2.request(i.method, i.url, **(i.kwargs)) as resp:
					content = await resp.read()
					myAhttp = Ahttp(content,resp)
					result.append(myAhttp)

		if i.callback:
			try:
				i.callback(myAhttp)
			except:
				pass
	except Exception as e:
		result.append(None)
		exception_handle and exception_handle(i, e)
		raise e
				
async def control_sem(sem, i, exception_handle, session ):
    # 限制信号量
    async with sem:
        await fetch(session, i, exception_handle)