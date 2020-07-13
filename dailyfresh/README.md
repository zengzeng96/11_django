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
sudo redis-server /etc/redis/redis.conf #指定加载的配置文件 必须以该命令启动redis服务不然的话就会报错
```



### worker在linux环境下工作

```python
celery -A celery_tasks.tasks worker -l info -P eventlet  # info打印出提示信息

```

## mysql链接远程数据库

```mysql
1、连接本地数据库

       mysql -u用户名  -p密码

      --默认连接主机为localhost，默认端口为3306

2、远程连接数据库，需指定连接的主机IP地址
      mysql -u用户名  -p密码  -h192.168.9.111
      表明连接到主机地址为  192.168.9.111，端口号为3306的Mysql数据库

3、一般情况下使用用户连接数据库时都会涉及到权限问题，需要赋权才能访问

      grant  select,update,delete  on  *.*   to   user@‘192.168.9.111’   identified by "密码";

      表示授予user用户可以通过192.168.9.111这台机器进行登录并赋予查询、更新、删除任何库任何表中的操作

      "*.*" ：第一个*表示数据库名称，第二个*表示表名，所有则用*代替

     如果允许用户在任何机器上登录，则将IP地址192.168.9.111换成“%”即可

     同时可以设定用户为无密码登录，根据笔者测试，发现只有设定用户可以在任何机器上登录时才能设置无密码登录

      grant  select,update,delete  on  *.*   to   user@‘%’   identified by "";

4、查看Mysql用户以及各用户允许登录机器信息

     1、使用root用户登录mysql数据库，

     2、 找到mysql数据库(use mysql)

     3、找到user表（show tables）

     4、可以查看里面的信息，主要看user,host,password(新版用authentication_string替换password)
```

### 通过源码来安装python包

```python
tar xvfz celery-0.0.0.tar.gz
cd celery-0.0.0
python setup.py build
python setup.py install
```

### 使用redis存储session 不使用mysql存储session

__缓存__:将数据存储在缓存里

```python
# Django的缓存配置  将下面的代码添加到项目的配置文件中 settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.176.130:6379/9",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 配置session存储
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### 开启ngix

```python
#开启服务
sudo service fdfs_trackerd start
sudo service fdfs_storaged start
sudo /usr/local/nginx/sbin/nginx

sudo /usr/local/nginx/sbin/nginx -s reload#重新启动nginx

```

### 安装依赖包

```python
#列出已安装的包
pip freeze or pip list

#导出requirements.txt
pip freeze > <目录>/requirements.txt
pip freeze > requirements.txt
```



### 静态页面的生成ngnix（网站性能的优化，减少数据库查询的次数，防止恶意的攻击）

```python
#模型管理类
#celery
#配置nginx的端口
```

### 数据缓存（网站性能的优化，减少数据库查询的次数，防止恶意的攻击（DDOS攻击））

把页面上使用到的数据放在缓存中，下次使用先从缓存获取，查不到再去数据库查询

**什么时候需要更新首页的缓存数据**

当管理员后台更新数据库时，需要更新缓存