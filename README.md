# celery-study
celery分布式学习记录
## 环境搭建
```bash
brew install redis
pip install redis
pip install celery
```
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

