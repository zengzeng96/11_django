# 使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import time

#创建一个Celery实例对象
app=Celery('celery_tasks.tasks',broker='redis://192.168.176.130:6379/8')
#1.里面这个字符串是随便写的 
#2.使用redis数据库的8号数据库


# 定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    """发送激活邮件"""
    '''组织邮件信息'''
    subject='天天生鲜欢迎信息'
    message=''
    sender=settings.EMAIL_FROM
    print('*'*10,sender,'*'*10)
    receiver=[to_email]
    html_message='<h1>%s,欢迎您成为天天生鲜注册会员。</h1>请点击下面链接激活您的账户:<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)
    send_mail( subject,message,sender,recipient_list=receiver,html_message=html_message)



