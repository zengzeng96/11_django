# -*- coding:utf-8 -*-
from django.http import HttpResponse

class BlockedIPMiddleware(object):
    '''中间件类   需要在setting中注册中间件类'''    
    EXCLUDE_IPS=['192.168.0.113']
    def process_view(self,request,view_func,*view_args,**kwargs):
        '''视图函数调用之前会调用它'''
        user_ip=request.META['REMOTE_ADDR']
        if user_ip in BlockedIPMiddleware.EXCLUDE_IPS:
            return HttpResponse("<h1>Forbidden</h1>")
            # else:
            #     return view_func(request,*args,**kwargs)

class TestMiddleware(object):
    """中间键类"""
    def __init__(self, *arg):
        '''服务器重启之后 接受第一个请求时调用 只调用一次 后面就不会再调用'''
        # super(TestMiddleware, self).__init__()

        print('__init__')

    def process_request(self,request):
        '''产生request对象之后 匹配url之前调用'''
        # 可以直接在这里直接返回一个Resposne 后面的process_view函数就不会再调用了  也不会再调用 视图函数了
        print('---process_request---')

    def process_view(self,request,view_func,*view_args,**kwargs):
        '''url匹配之前 视图函数调用之前'''

        print('---process_view---')

    def process_response(self,request,response):
        '''视图函数调用之后   内容返回浏览器之前'''
        print('---process_response---')
        return response

    
class ExceptionTest1Middleware(object):
    """视图函数发生异常时调用的函数"""
    def process_exception(self,request,exception):
        print(exception)
        print('----process_exception1----')

class ExceptionTest2Middleware(object):
    """视图函数发生异常时调用的函数"""
    def process_exception(self,request,exception):
        print('----process_exception2----')   


            
