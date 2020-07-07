from django.contrib import admin
from yuwenTest.models import BookInfo, HeroInfo
# Register your models here.
'''
#后台管理的文件
    语言和时区的设置
    修改settings.py文件

创建管理员
    命令：python manage.py createsuperuser
        创建用户名 这里先写成admin
        创建 邮箱地址  zengjia42@126.com
        创建 密码   090696

    创建好之后启动服务器
    python manage.py runserver
    可以登录页面
    http://127.0.0.1:8000/admin/
    帮助管理后台数据库的页面

注册模型类
    在admin.py中注册模型类
    对象在网页中的显示
        b=BookInfo.objects.get(btitle='天龙八部')
        str(b)    返回的内容就是在网页上显示的对象数据

'''
# 自定义模型管理类


class BookInfoAdmin(admin.ModelAdmin):
    '''图书模型管理类'''
    list_display = ['id', 'btitle', 'bpub_date']


class HeroInfoAdmin(admin.ModelAdmin):
    '''英雄人物模型管理类'''
    list_display = ['id', 'hname', 'hcomment']

admin.site.register(BookInfo, BookInfoAdmin)
admin.site.register(HeroInfo, HeroInfoAdmin)
# BookInfo object
