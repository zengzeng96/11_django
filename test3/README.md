# test3
- request.post 的类型是django.http.request.QueryDict类型   字典的子类
- 错误文件提示 debug=False   templates/404.html   就会调用我们自己的文件
- ajax登录  return JsonResponse({'res':1})  在不重新加载页面的情况下，对页面进行局部的刷新
- 异步的ajax请求 不等回调函数执行就向下执行js代码
- ajax请求在后台 不要返回页面或者重定向 通过回调函数来跳转  login_ajax_check()函数
- session与cookie的不同点就是 cookie 保存进去的是啥 取出来都是字符串   但是session保存进去是啥取出来就是啥
- request.session.clear()   数据库中的sessionid值还在   但是sessionid对应的值就已经不再了
- request.session.flush()   数据库中的sessionid值也删除了
- 删除session中的某个键值    del request.session['键']

