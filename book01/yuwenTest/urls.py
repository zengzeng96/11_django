#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2020-02-25 22:30:08
# @Author  : ZENG JIA (zengjia42@126.com)
# @Link    : https://weibo.com/5504445825/profile?topnav=1&wvr=6


# here import the lib
import sys
import os
import re
from django.conf.urls import url
from yuwenTest import views

urlpatterns = [
    # 通过url函数设置路由配置项
    url(r'^index$', views.index),  # 建立 /index 和视图之间的关系
    url(r'^index2$', views.index2),  # 严格匹配开头和结尾
    url(r'^books$', views.show_books) , # x显示图书信息
    url(r'^books/(\d+)$', views.detail),  # x显示英雄信息
    url(r'^detail-(\d+).html$', views.detail),  # x显示英雄信息
    # 在进行正则表达式对url进行匹配时  括号分组得到的内容会被当作参数传递给 后面对应的视图函数

]

def main():
    pass

if __name__ == "__main__":
    main()
