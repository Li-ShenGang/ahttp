## ahttp：基于协程的 Http 请求库
ahttp 是一个使用 aiohttp 和 asyncio 为基础进行封装的库，所有的http连接请求均使用协程的方式。 使请求过程中 IO 操作交给其他硬件，而CPU专注于处理计算型任务，可以大量的节约等待的时间。
## 快速上手 ##
### 安装 ###
你可以通过以下方式快速安装：


    pip install ahttp


### 使用 ###
使用是非常简单的：


	import ahttp
	
	urls = [
	    'http://www.heroku.com',
	    'http://python-tablib.org',
	    'http://httpbin.org',
	    'http://python-requests.org',
	    'http://fakedomain/',
	    'http://kennethreitz.com'
	]
	


然后创建一个任务列表：

	>>>tasks=(ahttp.get(i) for i in urls)

随后让这些url发出请求：

	>>>results=ahttp.run(tasks)
	[<ahttp [200]>, <ahttp [200]>, <ahttp [200]>, <ahttp [200]>, None, <ahttp [200]>]

可以看到，请求最终返回的是一个 aiohttp 类型的对象的集合

	<aiohttp [200]> # []中的数字200是状态码，200代表请求成功
获取返回的html可以这样：

	results[0].text() #获取第一个返回的html


**需要注意的是，如果你所请求的网址是属于同属于同一个域名，那么你可以通过使用Session的方式进行请求，这样连接的速度将会大幅度提高，请见 [使用Session](#session)**


## 基本使用 ##
### 发送请求 ###
- 导入模块

		import ahttp

- 把需要请求的连接添加到任务中

		urls = [
		    'http://www.heroku.com',
		    'http://python-tablib.org',
		    'http://httpbin.org',
		    'http://python-requests.org',
		    'http://fakedomain/',
		    'http://kennethreitz.com'
		]
	
		tasks=(ahttp.get(i) for i in urls)
		
- 或者，你可能需要构建这样的一组任务

		tasks=[ahttp.get(url1), ahttp.post(url2, data=data), ahttp.post(url3), ahttp.get(url4)]

- 然后，送他们去工作

		ahttp.run(tasks)

- 除了 POST 请求和 GET 请求之外，你也可以发送其他请求

		ahttp.put('http://httpbin.org/put', data=b'data')
		ahttp.delete('http://httpbin.org/delete')
		ahttp.head('http://httpbin.org/get')
		ahttp.options('http://httpbin.org/get')
		ahttp.patch('http://httpbin.org/patch', data=b'data')
### 响应内容 ###
- `results = ahttp.run(tasks)` 会让我们得到响应对象的集合

		[<ahttp [200]>, <ahttp [200]>, <ahttp [200]>, <ahttp [200]>, None, <ahttp [200]>]

- 我们现在取出其中一个响应的对象

		resp = results[0]
- 查看这个对象是哪个连接响应来的

		resp.url

- 查看响应的请求方式（POST, GET或者其他）

		resp.method

- 查看字节形式的响应文本

		resp.content

- 查看字符串形式响应的文本

		resp.text()

- 查看响应Cookies

		resp.cookies

- 查看响应状态码

		resp.status
- 查看响应头

		resp.headers
- 如果你对 aiohttp 这个协程http库比较熟悉，那么你也可以通过获得其原生的响应对象来获得想要的内容，原生的响应对象的方法和属性具体可参照 aiohttp 的官方文档

		resp.raw #返回原生响应对象

### 在URL中传递参数 ###
你可以通过以下几种方式给URL传递参数

- dict传参

		params1 = {'key1': 'value1', 'key2': 'value2'} 
		params2 = [('key', 'value1'), ('key', 'value2')]

		tasks=[ahttp.get(url, params = params1), ahttp.get(url, params = params2)]
- 字符串传参


		params1 = 'key1=value1&key2=value2'
		params2 = 'key3=value3&key4=value4'
		tasks=[ahttp.get(url, params = params1), ahttp.get(url, params = params2)]
		
- POST请求传递 json

		import json

		params = {'key1': 'value1', 'key2': 'value2'}
		tasks=[ahttp.get(url, params = json.dumps(params)), ]

### POST数据的几种方式 ###
- 模拟表单提交

		data = {'key1': 'value1', 'key2': 'value2'}
		
		tasks=[ahttp.post(url, data = data)]

- POST json 数据

		import json

		data = {'key1': 'value1', 'key2': 'value2'}
		tasks=[ahttp.get(url, data = json.dumps(data))]

- POST 文件和预压缩数据，请参考我的另一篇博客

		http://blog.csdn.net/getcomputerstyle/article/details/71515331

### <span id = "session">使用 Session</span> ###
>**Aiohttp建议使用ClientSession作为主要接口来发出请求。**ClientSession允许您在请求之间存储cookie，并保留所有请求（事件循环，连接和其他事件）通用的对象。

虽然 aiohttp 建议使用 ClientSession 来创建连接，**但是 ahttp 中并没有把它设置成默认开启的选项**，你必须通过手动的方式启用它。不过我是强烈建议使用开启Session来进行连接的，**在ahttp中开启session后，将使用keep-alive，能够很大大大程度上加快连接的速度**

- 你可以在创建任务之前，创建一个携带session的ahttp对象

		s_ahttp = ahttp.Session()

- 然后一切又和以前一样, 创建一个任务

		tasks = (s_ahttp.get(i) for i in urls)

- 使用的同一个 s_ahttp 则是使用的同一个session，这意味着它们有着共同的储存Cookie，或者你可能需要两群携带不同session的对象, 和一群不开启session的对象

		s_ahttp1 = ahttp.Session()
		s_ahttp2 = ahttp.Session()
		...
		task1 = [s_ahttp1.get(i) for i in urls1]
		task2 = [s_ahttp2.post(i) for i in urls2]
		task3 = [ahttp.get(i) for i in urls3]
		tasks = task1 + task2 + task3
		
		ahttp.run(tasks)

	不过使用两个Session对象当做任务去请求和两个分开是一样的，因为当有多个Session的时候，会分别执行，而中间的时间则会阻塞

### 自定义请求头 ###

- 自定义请求头可直接作为参数传递到对象中，为每一个连接赋予请求头
	
		headers = {'content-type': 'application/json'}
		...
		tasks = [ ahttp.get(url=url, headers=headers), ...]

- 如果你是定义的开启session的 s_ahttp 对象，你只能给这些请求设置一个公共的请求头

		headers = {'content-type': 'application/json'}
		...
		s_ahttp = ahttp.Session(headers = headers)

### 自定义 Cookie ###

- s_ahttp自定义Cookie

		cookies = {'content-type': 'application/json'}
		...
		s_ahttp = ahttp.Session(cookies = cookies)

- ahttp连接设置Cookie

		headers = {'PHPSESSIONID': '0XJFDFJJHFGKALDAS'}
		...
		tasks = [ ahttp.get(url=url, cookies=cookies), ...]

### 自定义 encoding

请求在被响应时，实际上是这样进行的

	await resp.read()

所以对于 ahttp 对象来说，拥有更快速度的是直接获取字节形式的文本

	results[0].content

但是如果你想获取字符串形式的文本

	results[0].text()

实际上在类的内部是这样工作的

	self.text(encoding = 'utf-8') = self.content.decode(encoding)

这意味着，默认情况下是使用 `utf-8` 进行解码的，如果你想使用其他的解码方式获取文本
	
	encoding = 'gb2312'
	
	self.text(encoding = encoding)

### Cookie安全性 ###

>默认ClientSession使用的是严格模式的 aiohttp.CookieJar. RFC 2109，明确的禁止接受url和ip地址产生的cookie，只能接受 DNS 解析IP产生的cookie。可以通过设置aiohttp.CookieJar 的 unsafe=True 来配置

ahttp的session模式继承了ClientSession的严格模式的cookie，你可以改为接收 url 和 ip 地址产生的cookie

	s_ahttp = ahttp.Session(unsafe = True)

### 设置代理 ###
- 无验证代理

		proxy = "http://some.proxy.com"
		...
		tasks = [ahttp(url, proxy = proxy), ...]

- 需要授权的代理

		proxy = "http://some.proxy.com"
		...
		tasks = [ahttp(url, proxy = proxy, proxy_auth=proxy_auth), ...]	

- 或者通过这种方式

		...
		tasks = [ahttp(url, proxy="http://user:pass@some.proxy.com"), ...]			

### 修改连接池的数量 ###
连接池的默认值为 2，意思是同时最多有 2 个协程及其周期在运转，你可以通过下列代码进行修改，但是请注意，不要超过1024个（我的电脑开到100的时候，风扇的声音特别响）。 如果服务器响应很慢，那么开的越多越好，可以改成 100 -200 ， 如果服务器响应很快，那么pool =2 和 pool = 100 几乎是没什么区别的。**因为等待都在 IO 操作上**

		...
		results = ahttp.run(tasks, pool = 100) #将连接池改为100

### 错误处理 ###
如果任务进行过程中出现错误，协程将不会终止，并且当前任务将会返回 None

	>>>results
	[<ahttp [200]>, None, <ahttp [200]>]

三个任务中，有一个出现了错误。 由于results不是按照任务的顺序返回的结果，所以为了捕捉究竟是哪个请求出现了错误，你可以传递一个错误处理函数

	def exception_handle(task, e): #出现错误时，将会把当前任务作为参数传递给错误处理函数, 第二个参数是错误对象
		print("在使用 " + task.method +" 方式向连接 " + task.url + " 进行请求时，出现了错误")
	...
	results = ahttp.run(tasks, exception_handle = exception_handle)

这样即使出错，我们也可以知道是谁出了问题

	>>>results = ahttp.run(tasks, exception_handle = exception_handle)
	在使用 POST 方式向连接 www.baidu.com 进行请求时，出现了错误
	[<ahttp [200]>, None, <ahttp [200]>]

或者，可以把请求过程中出错的请求收集起来，以便再次重试

	gather_err=[]
	def exception_handle(task):
		gather_err.append(task)
	...
	results = ahttp.run(tasks, exception_handle = exception_handle)
请求结束后，`gather_err` 这个 list 汇集了所有请求失败的对象，我们可以直接把这个 `gather_err` 作为任务再进行请求

	results1 = ahttp.run(gather_err)

因为 `gather_err` 和 `tasks` 一样，都是 `ahttp` 任务对象的集合

### 回调函数 ###
你可以通过给任务对象添加回调函数的方式以指定当前任务完成执行的函数

	def callback(ahttp_response):
		ahttp_response # <ahttp [200]>
		ahttp_response.status # 200
	...
	tasks=[ahttp.get(url, callback = callback), ...]
### 更新日记 ###

2017.11.11 version 1.0.0:

1.增加对单个协程请求的支持

2.修复原ahttp对象传递cookies和headers传递错误的Bug

3.修复多个session对象请求混乱的Bug

3.新增可维护的任务队列

4.原 ahttp.map() 方法废弃，改为 ahttp.run() 方法