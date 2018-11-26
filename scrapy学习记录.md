# scrapy-study
scrapy框架学习记录

# 一.常用命令
创建工程 scrapy startproject xx  
构建爬虫 scrapy genspider xx xx.org   名字加域名  
运行爬虫（不运行整个工程）scrapy runspider xx.py  
运行工程 scrapy crawl xx  


# 二.各文件简介及作用
创建tutorial工程   
* tutorial/  
    * scrapy.cfg  
    * tutorial/  
        * __init__.py  
        * items.py  
        * pipelines.py  
        * settings.py  
        * spiders/  
            * __init__.py  
            * xx.py  
            
* scrapy.cfg: 项目的配置文件. 
* tutorial/: 该项目的python模块。之后您将在此加入代码。 
* tutorial/items.py: 项目中的item文件. 
* tutorial/pipelines.py: 项目中的pipelines文件. 
* tutorial/settings.py: 项目的设置文件. 
* tutorial/spiders/: 放置spider代码的目录. 
* tutorial/spiders/xx.py: 爬虫文件.

# 三.配置
## settings.py 
ROBOTSTXT_OBEY值改为False  
添加 LOG_LEVEL = 'WARNING' 运行时只显示警告信息，否则会显示很多debug信息，影响阅读  
请求头根据具体需要添加

## 创建 run.py
写入  
from scrapy import cmdline  
cmdline.execute('scrapy crawl xx'.split())  
可以模拟终端输入运行而不需要从终端运行，方便调试和学习。

## items.py 
Item 是保存爬取到的数据的容器；其使用方法和python字典类似(或者说它就是字典)。 
例如： 
```python
class BiqugeItem(scrapy.Item):  
    name = scrapy.Field()  
    url = scrapy.Field() 
```
将需要获取的信息定义到类中，如果是多层次的信息（如先获取首页小说名和链接，再获取章节内容）可以定义多个类。 
通过定义item，可以很方便的使用Scrapy的其他方法。而这些方法需要知道item的定义。 


## xx.py(spider文件)
由指令可直接生成模板 
```python
class NovelSpider(scrapy.Spider):
    name = "novel"
    # allowed_domains = ["xx.org"]
    start_urls = ['https://www.xxbiquge.com/xclass/1/1.html']

    def parse(self, response):
        pass
```
其中：  
name：为爬虫名，唯一。  
allowed_domains： 指定爬取的域名范围。如在爬取腾讯新闻时可设置为["qq.com"] ，即可防止爬取到其他网站，比如各种广告。  
start_urls： 包含了Spider在启动时进行爬取的url列表。 因此，第一个被获取到的页面将是其中之一。 后续的URL则从初始的URL获取到的数据中提取。  
parse()： 是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。 

### parse()
```python
def parse(self, response):
books = response.xpath('//div[@class="l"]//li')
        for book in books:
            name = book.xpath('.//span[@class="s2"]//text()').extract()
            url = book.xpath('.//span[@class="s2"]//@href').extract()[0]
            url = 'https://www.xxbiquge.com/' + url

            item = BiqugeItem()
            item['name'] = name
            item['url'] = url
            # print(item)
            yield item
            yield scrapy.Request(url,callback=self.get_chapter)
```
parse()方法用于解析数据，可以使用xpath解析器和css解析器进行解析。由于获取到的是Response对象，所以与平常自己使用requests获取后解析不一样，可以直接使用xpath而不用先进行转换。解析完成后将数据传递给item，用yield循环抛出。如果还需再进行一次爬取，则用scrapy.Request()方法将需要传递的参数(例中为每本小说的url)传递给下一个自定义的parse()方法。 callback值为下一个方法名，也可以再调用自己，比如实现翻页操作。 
### 重点，很多时候需要在不同的parse中进行传值，此时可以使用meta,这是一个字典，使用方法如下：
```python
yield Request(url=url,meta={'au':copy.deepcopy(au)},callback=self.parse) #注意要用深拷贝(很多时候)
```
之前使用时au是item中的一个值，传递一直出错，发现item的值必须为字符串，而au为unicode，需要转换。谨记！

## 至此，一个运用scrapy框架进行爬取的爬虫已经初步完成。主要熟悉scrapy，只用到了最基础的，之后将会学习相关数据库，处理爬取到的数据等等，以及settings中各种参数的配置。



# ----------------华丽的分割线----------------
![图1](https://github.com/weizhimeng/scrapy-study/blob/master/1.png)
![图2](https://github.com/weizhimeng/scrapy-study/blob/master/2.png)

要想深入学习scrapy,必须要先了解它的工作流程。从上图可以清楚看到整个框架的流程和各个模块的职能以及各自间的配合，传递的参数。
## Scrapy Engine(Scrapy引擎)
核心，负责控制数据流在系统中所有的组件中流动，并在相应的动作发生时触发事件。类似与计算机的cpu，无需深入了解。
## Scheduler(调度器)
从引擎接受 request并让其入队，以便之后引擎请求它们时提供给引擎。
## pipelines.py
负责处理被spider提取出来的数据，可自定义类，同时需要修改settings文件使pieplines生效 (其中process_item()方法必须实现)
例如
```python
import json

class ItcastJsonPipeline(object):

    def __init__(self):
        self.file = open('test.json', 'wb')

    def process_item(self, item, spider):
        content = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(content)
        return item

    def close_spider(self, spider):
        self.file.close()
```
将数据存为json文件 

同时settings.py中
```python
#ITEM_PIPELINES = {
#    'biquge.pipelines.BiqugePipeline': 300,
#}
```
添加自己定义的类并将注释去掉。后面的数字代表优先度，数值越小优先度越高,通常在1-1000之间。
```python
ITEM_PIPELINES = {
    #'mySpider.pipelines.BiqugePipeline': 300,
    "mySpider.pipelines.ItcastJsonPipeline":1
}
```
## Spiders.py
我们主要需要编写的文件。Spider类定义了如何爬取某个(或某些)网站。包括了爬取的动作(例如:是否跟进链接)以及如何从网页的内容中提取结构化数据(爬取item)。 换句话说，Spider就是您定义爬取的动作及分析某个网页(或者是有些网页)的地方。 
对spider来说，爬取的循环类似下文:

1.以初始的URL初始化Request，并设置回调函数。 当该request下载完毕并返回时，将生成response，并作为参数传给该回调函数。

spider中初始的request是通过调用 start_requests() 来获取的。 start_requests() 读取 start_urls 中的URL， 并以 parse 为回调函数生成 Request 。

2.在回调函数内分析返回的(网页)内容，返回 Item 对象或者 Request 或者一个包括二者的可迭代容器。 返回的Request对象之后会经过Scrapy处理，下载相应的内容，并调用设置的callback函数(函数可相同)。

3.在回调函数内，您可以使用 选择器(Selectors) (您也可以使用BeautifulSoup, lxml 或者您想用的任何解析器) 来分析网页内容，并根据分析的数据生成item。

4.最后，由spider返回的item将被存到数据库(由某些 Item Pipeline 处理)或使用 Feed exports 存入到文件中。  
scrapy有四种基本选择器，xpath,css,extract和re,一般使用两种即可，建议使用xpath和正则。正则表达式较繁琐但平时用的很简单，而且大多常用的都可以网上搜到。xpath的使用写在下一个博客中。

## settings.py
最后就是配置文件的详细配置了，各项参数的设置可以大大提高爬取成功率和效率。以下为settings文件内容，加入了各项配置的描述。
```
# -*- coding: utf-8 -*-
 
# Scrapy settings for demo1 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
 
BOT_NAME = 'demo1'   #Scrapy项目的名字,这将用来构造默认 User-Agent,同时也用来log,当您使用 startproject 命令创建项目时其也被自动赋值。
 
SPIDER_MODULES = ['demo1.spiders']   #Scrapy搜索spider的模块列表 默认: [xxx.spiders]
NEWSPIDER_MODULE = 'demo1.spiders'   #使用 genspider 命令创建新spider的模块。默认: 'xxx.spiders'
 
 
#爬取的默认User-Agent，除非被覆盖
#USER_AGENT = 'demo1 (+http://www.yourdomain.com)'
 
#如果启用,Scrapy将会采用 robots.txt策略
ROBOTSTXT_OBEY = True
 
#Scrapy downloader 并发请求(concurrent requests)的最大值,默认: 16
#CONCURRENT_REQUESTS = 32
 
#为同一网站的请求配置延迟（默认值：0）
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs  
#DOWNLOAD_DELAY = 3   下载器在下载同一个网站下一个页面前需要等待的时间,该选项可以用来限制爬取速度,减轻服务器压力。同时也支持小数:0.25 以秒为单位
 
    
#下载延迟设置只有一个有效
#CONCURRENT_REQUESTS_PER_DOMAIN = 16   对单个网站进行并发请求的最大值。
#CONCURRENT_REQUESTS_PER_IP = 16       对单个IP进行并发请求的最大值。如果非0,则忽略 CONCURRENT_REQUESTS_PER_DOMAIN 设定,使用该设定。 也就是说,并发限制将针对IP,而不是网站。该设定也影响 DOWNLOAD_DELAY: 如果 CONCURRENT_REQUESTS_PER_IP 非0,下载延迟应用在IP而不是网站上。
 
#禁用Cookie（默认情况下启用）
#COOKIES_ENABLED = False
 
#禁用Telnet控制台（默认启用）
#TELNETCONSOLE_ENABLED = False 
 
#覆盖默认请求标头：
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}
 
#启用或禁用蜘蛛中间件
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'demo1.middlewares.Demo1SpiderMiddleware': 543,
#}
 
#启用或禁用下载器中间件
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'demo1.middlewares.MyCustomDownloaderMiddleware': 543,
#}
 
#启用或禁用扩展程序
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}
 
#配置项目管道
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'demo1.pipelines.Demo1Pipeline': 300,
#}
 
#启用和配置AutoThrottle扩展（默认情况下禁用）
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
 
#初始下载延迟
#AUTOTHROTTLE_START_DELAY = 5
 
#在高延迟的情况下设置的最大下载延迟
#AUTOTHROTTLE_MAX_DELAY = 60
 
 
#Scrapy请求的平均数量应该并行发送每个远程服务器
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
 
#启用显示所收到的每个响应的调节统计信息：
#AUTOTHROTTLE_DEBUG = False
 
#启用和配置HTTP缓存（默认情况下禁用）
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
```
解释几个常用的参数： 

ROBOTSTXT_OBEY = True-----------是否遵守robots.txt

CONCURRENT_REQUESTS = 16-----------开启线程数量，默认16

AUTOTHROTTLE_START_DELAY = 3-----------开始下载时限速并延迟时间

AUTOTHROTTLE_MAX_DELAY = 60-----------高并发请求时最大延迟时间 

DEPTH_LIMIT = 0-----------允许抓取任何网站的最大深度。如果为零，则不施加限制。 

DNSCACHE_ENABLED = True-----------是否启用DNS内存缓存。 

DNSCACHE_SIZE = 10000-----------DNS内存缓存大小。 

DNS_TIMEOUT = 60-----------以秒为单位处理DNS查询的超时。支持浮点。 

DOWNLOAD_DELAY = 0-----------下载器在从同一网站下载连续页面之前应等待的时间（以秒为单位）。这可以用于限制爬行速度，以避免击中服务器太难。支持小数。 

DOWNLOAD_TIMEOUT = 180-----------下载器在超时前等待的时间量（以秒为单位）。 

DOWNLOAD_MAXSIZE = 1073741824（1024MB）-----------下下载器将下载的最大响应大小（以字节为单位）。如果要禁用它设置为0(某些网站可能会发送一些很大的垃圾数据给爬虫)。 



请求头的设置之前已经叙述过，建议请求头一定要修改。或者预先定义一个请求头列表，每次爬取随机选择一个来使用，可以大大提高成功率。 其余的可根据需要自行配置（如log配置），还有一些应用在分布式爬取中，以后学习使用分布式的时候可参考官方文档。


## scrapy的大致用法就是以上这些了，一些小的项目还是自己编写代码比较灵活，大型的项目可以选择scrapy框架，而且日后学习分布式后用处更大。（毕竟自带分布式）

## scrapy的部署
最后便是爬虫的部署了，需要一台服务器。然后，安装scrapy专属的scrapyd和scrapyd-client 
```
pip install scrapyd　
pip install scrapyd-client
```
一路cd到scrapyd目录下，打开scrapyd.conf文件,将绑定ip修改为0.0.0.0，esc然后:wq保存退出，这样就可以远程访问了，否则只能本地访问。然后进入spiders目录，输入命令scrapyd启动，再在浏览器里输入服务器ip：6800即可看到部署成功后的结果。非常简单。唯一的问题就是scrapy的日志，一旦LOG_STDOUT设置为True将输出结果重定向到日志内，scrapyd步骤时就会出错，未找到解决办法。这样日志会非常冗长，并且预先做的异常处理无法看到结果。









