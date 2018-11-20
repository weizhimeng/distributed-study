# distributed-study
分布式学习记录
## 相关网址
Celery 官网：http://www.celeryproject.org/

Celery 官方文档英文版：http://docs.celeryproject.org/en/latest/index.html

Celery 官方文档中文版：http://docs.jinkan.org/docs/celery/ 

分布式队列神器 Celery：https://segmentfault.com/a/1190000008022050

celery最佳实践：https://my.oschina.net/siddontang/blog/284107

Celery 分布式任务队列快速入门：http://www.cnblogs.com/alex3714/p/6351797.html

异步任务神器 Celery 快速入门教程：https://blog.csdn.net/chenqiuge1984/article/details/80127446

定时任务管理之python篇celery使用：http://student-lp.iteye.com/blog/2093397

异步任务神器 Celery：http://python.jobbole.com/87086/

celery任务调度框架实践：https://blog.csdn.net/qq_28921653/article/details/79555212
## 环境搭建(celery)
```bash
brew install redis
pip install redis
pip install celery
```
## 使用
安装比较简单，之后先用redis-server & 命令后台开启redis服务(默认端口为6379)，然后写两个脚本测试
```python
#tasks.py
#coding:utf-8
import time
from celery import Celery

broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379/0'

app = Celery('my_task', broker=broker, backend=backend)

@app.task
def add(x, y):
    time.sleep(5)     # 模拟耗时操作
    return x + y
```

```python
#trigger.py
#coding:utf-8
from tasks import add
# 异步任务
add.delay(2,8)
print 'hello world'
```
在当前目录下运行celery worker -A tasks --loglevel=info，可以看到有日志输出，再直接运行trigger.py脚本，这里出现问题了
```bash
AttributeError: 'float' object has no attribute 'iteritems'
```
后在celery的github上的评论中找到问题所在，是redis的版本不兼容，此时我安装的最新版本为3.0.0，需要回退
```bash
pip install redis==2.10.6
```
重启服务，可以看到正确结果了： 

![](https://github.com/weizhimeng/celery-study/blob/master/1.png) 
可以看到，add函数需要等待5秒才返回执行结果，但由于它是一个异步任务，不会阻塞当前的主程序，所以print语句会直接打印出来而不用等待5秒。  
将第一个脚本部署到其他服务器上，后一个脚本在本机运行即可实现一个最简单的分布式。

## 使用scrapy-redis
安装后首先在settings.py中增加:
```python
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
#去重机制
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_HOST = '192.168.75.50'
REDIS_PORT = 6379
```
然后就可以部署到不同服务器上了，使用命令scrapy crawl xx 即可开启分布式爬取，相比celery使用更简单。原理也很简单，原先的scrapy的request队列是单机的，所以只能单个主机跑，而以上设置就是将request队列存放到redis中，这下便可以多个主机通过网络共享爬取队列，再通过redis的去重处理，便可实现分布式爬取。


