# 使用celery
import time

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.template import loader, RequestContext

import os
# import django
# #*******************************设置初始化 必须进行 在任务处理者一端加入 *********************************
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# django.setup()
# #*******************************设置初始化 必须进行  在任务处理者一端加入（linux端）*********************************
# 创建一个Celery实例对象
app = Celery('celery_tasks.tasks', broker='redis://192.168.176.134:6379/8')


# 1.里面这个字符串是随便写的
# 2.使用redis数据库的8号数据库3


# 定义任务函数
# @app.task
# def send_register_active_email():
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    '''组织邮件信息'''
    print('*' * 10, 'celery', '*' * 10)
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    print('*' * 10, sender, '*' * 10)
    receiver = [to_email]
    html_message = '<h1>%s,欢迎您成为天天生鲜注册会员。</h1>请点击下面链接激活您的账户:<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    send_mail(subject, message, sender, recipient_list=receiver, html_message=html_message)
    # time.sleep(5)

@app.task
def generate_static_index_html():
    """产生首页静态页面"""
    print("**"*20,'windows')
    types = GoodsType.objects.all()
    # 获取首页轮播商品信息
    goods_banner = IndexGoodsBanner.objects.all().order_by('index')  # 数字小的在前
    # 获取首页促促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页商品分类商品展示信息
    # type_goods_banners = IndexTypeGoodsBanner.objects.all()
    for type in types:  # GoodsType对象
        # 获取type种类首页分类商品的有图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 动态给对象增加属性 分别保存首页分类展示的图片和文字展示信息
        type.image_banners = image_banners
        # 获取type种类首页分类商品的有文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        type.title_banners = title_banners
    # 组织模板上下文
    context = {
        'types': types,
        'goods_banner': goods_banner,
        'promotion_banners': promotion_banners
    }
    # 1.加载模板文件
    temp = loader.get_template('static_index.html')
    # 2.定义模板上下文
    # context = RequestContext(request, context)
    # 3.模板渲染
    static_index_html = temp.render(context)

    # 生成首页对应的静态文件
    save_path=os.path.join(settings.BASE_DIR,'static/index.html')
    with open(save_path,'w') as f:
        f.write(static_index_html)

