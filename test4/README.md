# 模板文件 test4

##  模板变量
- {{}}        {% %}

- ```forloop.counter```   循环计数

- 模板语言过滤器
    ```python
    {{ book.btitle|length }}--{{ book.bpub_date|date:'b.d, Y'}}
    1.只有一个参数的过滤器
    book.id|mod
    2.有两个参数的过滤器
    book.id|mod_val:3
    自定义的过滤器至少有一个参数 这个版本只讲了一个过滤器 没有讲其他的过滤器  目前这个讲的只能最多有两个参数
    但是实际上是有具有多个参数的过滤器的
    
    48g版本有讲多种过滤器
    
    ```
    
- 模板语言-自定义过滤器
    装饰器的使用 
    
    ```
    http://python.usyiyi.cn/documents/django_182/ref/templates/builtins.html
    只有一个参数的过滤器 过滤器前面的对象就是过滤器的参数   有两个参数的过滤器就 过滤器的第一个参数就是过滤器前面的模版变量 第二个参数就是通过冒号写在过滤器后面的参数
    ```
    
- 模板语言的注释
1.单行注释：```{# 注释内容 #}```
2.多行注释：
  
  ```
{% comment %}
注释内容
  {% comment %}
  ```
  
- 模板继承（把所有文件都相同的页面写进父模版文件中）
    ```
    {% extends 'booktest/base.html' %}
	# 不同的内容需要在父模版中预留相应的块
	父模版中：
	
    {% block b2 %}
    <h1>这是父模板b2块中的内容</h1>
    {% endblock b2 %}
    
    字模版中：
    {% block b2 %}
    {{ block.super }}#获取父模版中该板块的默认内容
    <h1>这是子模板b2块中的内容</h1>
    {% endblock b2 %}
    ```

- html转义

  ```
   {{content|safe}}
   
   {% autoescape off %}
   {{content}}
   {% endautoescape %}
   
   模板硬编码 默认不会经过转义<br/>
   {{ test|default:'<h1> hello </h1>' }}
  
   模板硬编码 手动进行转义<br/>
   {{ test|default:'&lt;h1&gt; hello &lt;/h1&gt;' }}
  ```

- csrf攻击

  1.登录正常网站之后，浏览器保存了sessionid并且没有退出

  2.不小心访问了另一个网站并且点击了页面上的按钮

  3.django默认启用了csrf保护
  
  - __csrf防御原理__
  
    1) 渲染模板文件时在页面生成一个名字叫做__csrfmiddlewaretoken__的隐藏域
  
    2) 服务器交给浏览器保存一个名字为__csrftoken的cookie信息__
  
    3) 提交表单时，两个值都会发给服务器，服务器进行比对，如果一样，则csrf验证通过，否则失败

- 验证码

  __防止暴力请求__

  直接把代码沾过来就行

  ## url反向解析

  对于需要多次重定向的网页 一旦urls它的url改变的话，那么其余需要重定向到该页面的网站就的网址就都需要重写

  那么此时可以这样做：

  ```python
  url(r'^', include('booktest.urls',namespace='booktest')),【test4/】
  url(r'^index3$', views.index,name='index'),【booktest/urls.py】
  
  url反向解析生成index链接
  <a href="{% url 'booktest:index'%}">首页</a><br/>
  
  url(r'^show_args/(\d+)/(\d+)$', views.show_args,name='show_args'),  #捕获位置参数
  <a href="{% url 'booktest:show_args' 1 2 %}">show_args/1/2</a><br/>
  
  url(r'^show_kwargs/(?P<c>\d+)/(?P<d>\d+)$', views.show_kwargs,name='show_kwargs'),  #捕获关键字参数
  <a href="{% url 'booktest:show_kwargs' c=3 d=4 %}">show_kwargs/3/4</a><br/>
  
  
  【views.py】中的写法
  from django.core.urlresolvers import reverse
  # /test_redirect
  def test_redirect(request):
      '''重定向到首页'''
      # 在视图中反向解析
      # url=reverse('booktest:index')#动态产生的重定向首页地址
      
      # 重定向到/show_args/1/2
      # url=reverse('booktest:show_args' ,args=(1,2))#捕获位置参数
      
      # 重定向到/show_kwargs/3/4
      url=reverse('booktest:show_kwargs' ,kwargs={'c':3,'d':4})#捕获关键字参数
      return redirect(url)
  ```

-  静态文件(test3)

  ```
  动态获取static_url,拼接静态文件路径<br>
  <img src="{% static 'images/mm.jpg'%}">
  
  ```

- 中间件（test3）

  获取浏览器端的ip地址

  ```python
  user_ip	=	request.META['REMOTE_ADDR']
  
  ```

  中间件

  ```python
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
          
          
  如果注册的多个中间件类中包含process_exception函数的时候，调用的顺序跟注册的顺序是相反的。
  
  ```

- 后台管理(test3)

  管理员名称：admin

  管理员密码：123456#以后都写这个

  

  