#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
作者：李C
邮箱：cszy2013@163.com
'''

from functools import partial, wraps
from random import random
import asyncio, os
from aiohttp.helpers import deprecated_noop
from cchardet import detect
try:
	import aiohttp
except ImportError:
    raise RuntimeError('您没有安装aiohttp，请执行安装命令 pip install aiohttp  ')	

if os.name is not 'nt':
	try:
		import uvloop
	except:
		print('检测到您未安装uvloop, ahttp将使用默认引擎aiohttp作为时间循环。\n鉴于uvloop拥有更快的事件循环速度，请您安装uvloop，安装方法：\npip install uvloop')
	else:
		asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
		
	
__all__ = (
    'map',  'Session', 
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'session', 'request'
)

result, all_tasks, connector, sessiondict = [],[],[],{}

class AhttpRequest():
	def __init__(self, method, url, timeout=None, session=False, headers=None, cookies=None, unsafe=None, mark='1111111111', **kwargs):
		self.method, self.session, self.url, self.mark, self.timeout = method, session, url, mark, timeout
		callback = kwargs.pop('callback', None)
		self.callback = callback
		self.kwargs = kwargs
		if not session:
			self.sessiondict = (cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None)
	def run(self, pool=5, exception_handle = None):
		result = run([self], pool=pool, exception_handle=exception_handle)
		return result[0]

class WithSession():
	def __init__(self, mark, session=True):
		self.get = partial(AhttpRequest, 'GET', session=session, mark=mark)
		self.options = partial(AhttpRequest, 'OPTIONS', session=session, mark=mark)
		self.head = partial(AhttpRequest, 'HEAD', session=session, mark=mark)
		self.post = partial(AhttpRequest, 'POST', session=session, mark=mark)
		self.put = partial(AhttpRequest, 'PUT', session=session, mark=mark)
		self.patch = partial(AhttpRequest, 'PATCH', session=session, mark=mark)
		self.delete = partial(AhttpRequest, 'DELETE', session=session, mark=mark)
	
get = partial(AhttpRequest, 'GET')
options = partial(AhttpRequest, 'OPTIONS')
head = partial(AhttpRequest, 'HEAD')
post = partial(AhttpRequest, 'POST')
put = partial(AhttpRequest, 'PUT')
patch = partial(AhttpRequest, 'PATCH')
delete = partial(AhttpRequest, 'DELETE')

class ClientSession(aiohttp.ClientSession):
	def close(self):
		"""
		对ClientSession类的close方法进行重写
		"""
		if not self.closed:
			if self._connector_owner:
				self._connector.close()
			connector.append(self._connector)

		return deprecated_noop('ClientSession.close() is a coroutine')
def Session(cookies = None, headers = None, unsafe = None):
	mark = str(round(random()*10**10))
	sessiondict[mark] = (cookies, headers, aiohttp.CookieJar(unsafe=True) if unsafe else None)
	return WithSession(mark=mark)
	
def run(tasks, pool=2, exception_handle = None):
	del result[:]
	del connector[:]
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future( go(tasks, pool, exception_handle, loop=loop) )
	loop.run_until_complete(future)
	#loop.close()
	return result

class AhttpResponse():
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
	
	def text(self, encoding = None):
		encoding = encoding or detect(self.content)['encoding']
		return self.content.decode(encoding=encoding)

	def __repr__(self):
		return "<AhttpResponse [status {}]>".format(self.clientResponse.status)

	__str__=__repr__

async def go(tasks, pool, exception_handle, loop):
	del all_tasks[:]
	conn = aiohttp.TCPConnector(use_dns_cache=True, loop=loop, verify_ssl=False)
	sem = asyncio.Semaphore(pool)
	classify={}
	[ classify[i.mark].append(i) if classify.get(i.mark, 0) else classify.setdefault(i.mark,[i]) for i in tasks ]
	try:
		for i in classify.pop('1111111111'):
			all_tasks.append( control_sem(sem, i , exception_handle, session=False) )
	except:
		pass
	for i in classify:
		async with ClientSession( cookies=sessiondict[i][0], headers=sessiondict[i][1], cookie_jar=sessiondict[i][2], connector_owner=False, connector=conn ) as locals()['session{}'.format(i)]:
			for j in classify[i]:
				all_tasks.append(  control_sem(sem, j , exception_handle, session=locals()['session{}'.format(i)])  )

	await asyncio.wait( all_tasks )
	#关闭所有连接
	for i in connector:
		i.close()
	return True

async def fetch(session, i, exception_handle):
	try:
		if session:
			async with session.request(i.method, i.url, timeout=i.timeout, **(i.kwargs)) as resp:
				content = await resp.read()
				myAhttp = AhttpResponse(content,resp)
		else:
			async with aiohttp.ClientSession( cookies = i.sessiondict[0] , headers = i.sessiondict[1], cookie_jar = i.sessiondict[2] ) as session2:
				async with session2.request(i.method, i.url, timeout=i.timeout, **(i.kwargs)) as resp:
					content = await resp.read()
					myAhttp = AhttpResponse(content,resp)
					
		if i.callback:
			try:
				i.callback(myAhttp)
			except:
				pass
	except Exception as e:
		myAhttp = None
		exception_handle and exception_handle(i, e)

	finally:
		result.append(myAhttp)
				
async def control_sem(sem, i, exception_handle, session ):
    # 限制信号量
	async with sem:
		await fetch(session, i, exception_handle)