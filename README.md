## ahttp：简单、高效、异步requests请求模块
ahttp 是一个所有的http连接请求均使用协程的方式。 使请求过程中 IO 操作交给其他硬件，而CPU专注于处理计算型任务，可以大量的节约等待的时间。

**适用版本： PYTHON 3.7**

## 快速开始 ##
### 安装 ###
你可以通过以下方式快速安装：


    pip install ahttp

### 单个请求 ###
使用是非常简单的：
```
import ahttp 

url = "http://httpbin.org/headers" 
```
构造一个get请求对象：
```
req = ahttp.get(url)
```
执行请求：
```
res = res.run()
```
打印出请求得到的文本：
```
print(res.text)
```



> 如果你使用过requests，那么ahttp的使用方式基本上和它一致，只不过requests请求是同步，而ahttp的请求是异步。不同的是requests可以直接请求，而由于ahttp是异步的，所以需要构造好请求之后进行一次“执行”

### 多个请求 ###
单个请求的时候，ahttp的异步是无法体现出来的，多个请求的时候则能很好的体现异步的不同和快速

构造一些请求(这里以获取 [豆瓣电影排行250](https://movie.douban.com/top250?start=0) 为例)：
```
urls = [ f"https://movie.douban.com/top250?start={i*25}" for i in range(10) ]
reqs = [ahttp.get(url) for url in urls]
```
这里的`reqs`里存放了10个请求对象，但是还未执行请求，通过`ahttp.run(reqs)`执行这些请求：
```
resps = ahttp.run(reqs)
```
运行上面命令后，这10个请求会以异步的形式执行，打印执行结果：
```
print(resps)

#输出结果如下：
[<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=0]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=25]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=75]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=50]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=100]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=125]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=150]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=175]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=200]>, 
<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=225]>]
```
查看第一个请求的html：
```
print(resps[0].text)
```
### 多个请求（使用session）
和使用ahttp构造请求list请求相比，使用session请求速度更快，而且共享cookies，因为session创建的是一个持久的链接：

```
urls = [ f"https://movie.douban.com/top250?start={i*25}" for i in range(10) ]
sess = ahttp.Session()
reqs = [sess.get(url) for url in urls]

resps = ahttp.run(reqs)
print(resps)
```
输出结果如下：
```
[<AhttpResponse status[200] url=[https://movie.douban.com/top250?start=25]>,
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=50]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=75]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=0]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=100]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=125]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=150]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=175]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=225]>, 
 <AhttpResponse status[200] url=[https://movie.douban.com/top250?start=200]>]
```
### 有序返回
`reqs`列表完成请求之后，得到的是一个`resps`列表。由于是异步请求，所以得到的`resps`并不是按照`reqs`请求的顺序排列的。豆瓣排行我们需要按照顺序处理，只需要在`ahttp.run`添加一个参数`order`
```
resps = ahttp.run(reqs, order=True)
```
### 提取文本
ahttp内置了使用requests_html来处理文本，使文本处理非常的简单
例如提取第一个链接中的电影title：
```
resp = resps[0]
titles =[i[0] for i in resp.html.search_all('<span class="title">{}</span>')]
```
得到的结果如下：
```
['蝙蝠侠：黑暗骑士', '&nbsp;/&nbsp;The Dark Knight', '活着', '控方证人', 
'&nbsp;/&nbsp;Witness for the Prosecution', '乱世佳人', '&nbsp;/&nbsp;Gone with the Wind', '少年派的奇幻漂流',
 '&nbsp;/&nbsp;Life of Pi', '摔跤吧！爸爸', '&nbsp;/&nbsp;Dangal', '指环王3：王者无敌', 
 '&nbsp;/&nbsp;The Lord of the Rings: The Return of the King', '飞屋环游记', 
 '&nbsp;/&nbsp;Up', '鬼子来了', '十二怒汉', '&nbsp;/&nbsp;12 Angry Men', '天空之城', 
 '&nbsp;/&nbsp;天空の城ラピュタ', '天堂电影院', '&nbsp;/&nbsp;Nuovo Cinema Paradiso', '寻梦环游记', '&nbsp;/&nbsp;Coco', '大话西游之月光宝盒',
  '&nbsp;/&nbsp;西遊記第壹佰零壹回之月光寶盒', '末代皇帝', '&nbsp;/&nbsp;The Last Emperor', '哈尔的移动城堡', '&nbsp;/&nbsp;ハウルの動く城',
   '罗马假日', '&nbsp;/&nbsp;Roman Holiday', '搏击俱乐部', '&nbsp;/&nbsp;Fight Club',
    '闻香识女人', '&nbsp;/&nbsp;Scent of a Woman', '素媛', '&nbsp;/&nbsp;소원', '辩护人', 
    '&nbsp;/&nbsp;변호인', '窃听风暴', '&nbsp;/&nbsp;Das Leben der Anderen', '何以为家', 
    '&nbsp;/&nbsp;كفرناحوم', '死亡诗社', '&nbsp;/&nbsp;Dead Poets Society', '两杆大烟枪', 
    '&nbsp;/&nbsp;Lock, Stock and Two Smoking Barrels']
```

> 有关更多文本处理，请参考 [requests_html](https://github.com/psf/requests-html) 文本处理

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

		[<AhttpResponse [status 200]>, <AhttpResponse [status 200]>, <AhttpResponse [status 200]>, <AhttpResponse [status 200]>, None, <AhttpResponse [status 200]>]

- 我们现在取出其中一个响应的对象

		resp = results[0]
- 查看这个对象是哪个连接响应来的

		resp.url

- 查看响应的请求方式（POST, GET或者其他）

		resp.method

- 查看字节形式的响应文本

		resp.content

- 查看字符串形式响应的文本

		resp.text

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
		tasks=[ahttp.get(url, json=data)
- POST 文件和预压缩数据，请参考我的另一篇博客

		http://blog.csdn.net/getcomputerstyle/article/details/71515331

### <span id = "session">使用 Session</span> ###

**使用session后，将使用keep-alive，能够很大大大程度上加快连接的速度**

- 你可以在创建任务之前，创建一个携带session的ahttp对象

		sess = ahttp.Session()

- 然后一切又和以前一样, 创建一个任务

		tasks = (sess.get(i) for i in urls)

- 使用的同一个sess 则是使用的同一个session，它们有着共同的Cookie，不同的session请求对象也可以一起发出请求

		sess1 = ahttp.Session()
		sess2 = ahttp.Session()
		...
		task1 = [sess1.get(i) for i in urls1]
		task2 = [sess2.post(i) for i in urls2]
		task3 = [ahttp.get(i) for i in urls3]
		tasks = task1 + task2 + task3
		
		ahttp.run(tasks)



### 创建单个请求 ###

	task = ahttp.get('https://www.google.com')
	task.run()

或者可以这样写

	result = ahttp.get('https://www.google.com').run()

### 自定义请求头 ###

- 自定义请求头可直接作为参数传递到对象中，为每一个连接赋予请求头
	
		headers = {'content-type': 'application/json'}
		...
		tasks = [ ahttp.get(url=url, headers=headers), ...]

- 给session设置请求头

		headers = {'content-type': 'application/json'}
		...
		sess = ahttp.Session()
		sess.headers = {
			...
		}

### 自定义 Cookie ###

- session自定义Cookie

		cookies = {'content-type': 'application/json'}
		...
		sess = ahttp.Session()
		sess.cookies = {...}

- ahttp连接设置Cookie

		headers = {'PHPSESSIONID': '0XJFDFJJHFGKALDAS'}
		...
		tasks = [ ahttp.get(url=url, cookies=cookies), ...]

### 自定义 encoding

ahttp采用了自动识别的编码方式，能够自动识别的编码如下：

国际（Unicode）
UTF-8
UTF-16BE / UTF-16LE
UTF-32BE / UTF-32LE / X-ISO-10646-UCS-4-34121 / X-ISO-10646-UCS-4-21431
阿拉伯
ISO-8859-6
WINDOWS-1256
保加利亚语
ISO-8859-5
WINDOWS-1251
中文
ISO-2022-CN
BIG5
EUC-TW
GB18030
HZ-GB-2312
克罗地亚：
ISO-8859-2
ISO-8859-13
ISO-8859-16
Windows的1250
IBM852
MAC-CENTRALEUROPE
捷克
Windows的1250
ISO-8859-2
IBM852
MAC-CENTRALEUROPE
丹麦
ISO-8859-1
ISO-8859-15
WINDOWS-1252
英语
ASCII
世界语
ISO-8859-3
爱沙尼亚语
ISO-8859-4
ISO-8859-13
ISO-8859-13
Windows的1252
Windows的1257
芬兰
ISO-8859-1
ISO-8859-4
ISO-8859-9
ISO-8859-13
ISO-8859-15
WINDOWS-1252
法国
ISO-8859-1
ISO-8859-15
WINDOWS-1252
德语
ISO-8859-1
WINDOWS-1252
希腊语
ISO-8859-7
WINDOWS-1253
希伯来语
ISO-8859-8
WINDOWS-1255
匈牙利：
ISO-8859-2
WINDOWS-1250
爱尔兰盖尔语
ISO-8859-1
ISO-8859-9
ISO-8859-15
WINDOWS-1252
意大利
ISO-8859-1
ISO-8859-3
ISO-8859-9
ISO-8859-15
WINDOWS-1252
日本
ISO-2022-JP
SHIFT_JIS
EUC-JP
朝鲜的
ISO-2022-KR
EUC-KR / UHC
立陶宛
ISO-8859-4
ISO-8859-10
ISO-8859-13
拉脱维亚
ISO-8859-4
ISO-8859-10
ISO-8859-13
马耳他语
ISO-8859-3
抛光：
ISO-8859-2
ISO-8859-13
ISO-8859-16
Windows的1250
IBM852
MAC-CENTRALEUROPE
葡萄牙语
ISO-8859-1
ISO-8859-9
ISO-8859-15
WINDOWS-1252
罗马尼亚：
ISO-8859-2
ISO-8859-16
Windows的1250
IBM852
俄语
ISO-8859-5
KOI8-R
WINDOWS-1251
MAC-CYRILLIC
IBM866
IBM855
斯洛伐克
Windows的1250
ISO-8859-2
IBM852
MAC-CENTRALEUROPE
斯洛文尼亚
ISO-8859-2
ISO-8859-16
Windows的1250
IBM852
中号

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
- socks代理

		proxy = {
		    "http":"socks5://127.0.0.1:1080",
		    "https":"socks5h://127.0.0.1:1080"
		}
		ahttp.get(url, proxy=proxy)

### 修改最大并发的数量 ###
连接池的默认值为 2，意思是同时最多有 2 个协程及其周期在运转，你可以通过下列代码进行修改，但是请注意，不要超过1024个。 如果服务器响应很慢，那么开的越多越好，可以改成 100 -200 ， 如果服务器响应很快，那么pool =2 和 pool = 100 几乎是没什么区别的。**因为等待都在 IO 操作上**

		...
		results = ahttp.run(tasks, pool = 100) #将连接池改为100

### 回调函数 ###
你可以通过给任务对象添加回调函数的方式以指定当前任务完成执行的函数

	def callback(ahttp_response):
		ahttp_response # <AhttpResponse [status 200]>
		ahttp_response.status # 200
	...
	tasks=[ahttp.get(url, callback = callback), ...]

### 设置超时 ###

	task = ahttp.get(url,..., timeout=300)
	# timeout 默认300s

## 欢迎 fork 并提交您的优化代码