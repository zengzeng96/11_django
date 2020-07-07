from django.db import models
from mongoengine import *

# Create your models here.
# ORM
# from mongoengine import connect

# connect('douban', host='127.0.0.1', port=27017)


class ArticleInfo(Document):
    # = ListField()
    # 名字必须严格与数据库里的字段一样
    serial_number = StringField()
    origin_url = StringField()
    movie_name = StringField()
    describe = StringField()
    star = StringField()
    evalulate = StringField()
    introduce = ListField()  # 列表结构

    meta = {  # 在数据库已经存在的情况下就必须要加
        # 如果是新建数据库 就不用写这个选项
        'collection': 'top250'
    }


for i in ArticleInfo.objects:
    print(i.movie_name)
