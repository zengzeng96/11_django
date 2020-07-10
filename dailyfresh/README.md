# dailyfresh项目

## 将apps的路径加入系统搜索路径中

code:编辑setting.py文件

```python
import sys
sys.path.insert(0,os.path.join(BASE_DIR,'apps'))
#这样在配置项目的时候 就只需要写项目的名称而不需要写 apps.user
```

## 将用户信息进行加密

```python
pip install itsdangerous

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

```

## 邮件的发送

- 第一种写法是同步的邮件发送 需要等待较长的时间
- 第二种 异步发送邮件（celery）

```python
# 查看进程
ps aux | grep redis#查看redis进程
redis-cli -h 192.168.176.130 -p 6379#链接远程的redis数据库
sudo kill -9 进程号#杀死某个进程
```



