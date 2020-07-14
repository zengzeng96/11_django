from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection

from goods.models import GoodsSKU
from utils.mixin import LoginRequiredMixin

# Create your views here.
# ajax发起的请求都在后台 在浏览器中看不到效果

#购物车总件数 总是通过数据库查询传回的

# /cart/add
class CartAddView(View):
    """购物车记录添加"""

    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            # 用户未登陆
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 涉及到数据库数据的修改 需要进行post传参
        '''购物车记录添加'''
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        # 业务处理：添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 先尝试sku_id的值
        cart_count = conn.hget(cart_key, sku_id)  # 如果sku_id在hash中不存在 hget不会报错 而是会返回None
        if cart_count:
            # 累加购物车中商品的数量
            count += int(cart_count)
        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        # 设置hash中sku_id对应的值 存在就更新 不存在就添加
        conn.hset(cart_key, sku_id, count)
        # 计算用户购物车中商品的条目数
        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res': 5, 'message': '添加成功', 'total_count': total_count})


# /cart
class CartInfoView(LoginRequiredMixin, View):
    '''购物车页面显示'''

    def get(self, request):
        """显示"""

        # 获取登录的用户
        user = request.user
        # 获取用户购物车中商品的信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        cart_dict = conn.hgetall(cart_key)  # 返回的字典的格式{'商品id':'商品数量'}
        # 遍历获取商品的信息
        skus = []
        # 保存用户购物车中商品的总数目与总价格
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku对象添加属性  保存商品的小计
            sku.amount = amount
            # 动态给sku对象添加属性 count  保存商品的数量
            sku.count = count
            skus.append(sku)

            # 累加计算商品的总数目和总金额
            total_count += int(count)
            total_price += amount
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus
        }
        # 使用模版
        return render(request, 'cart.html', context)


# 更新购物车记录
# 采用ajax请求  设计数据修改 post
# 前端需要传递的参数：商品 sku_id   更新的商品数量


# /cart/update
class CartUpdateView(View):
    """购物车记录更新"""

    def post(self, request):
        '''购物车记录更新'''
        user = request.user
        if not user.is_authenticated():
            # 用户未登陆
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接受数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        # 业务处理：更新购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        # 更新
        conn.hset(cart_key, sku_id, count)
        # 计算用户购物车中的商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)
        # 返回应答
        return JsonResponse({'res': 5, 'message': '购物车更新成功', 'total_count': total_count})

# 删除购物车记录
# 采用ajax post请求
# 前端需要传递的参数   sku_id
# /cart/delete
class CartDeleteView(View):
    """购物车记录的删除"""
    def post(self,request):
        '''购物车记录删除'''
        #判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登陆
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        sku_id=request.POST.get('sku_id')
        # 数据的校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        #校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

        #业务处理 删除购物车记录
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id
        # 删除  hdel
        conn.hdel(cart_key,sku_id)

        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)
        # 返回应答
        return JsonResponse({'res': 3, 'message': '购物车更新成功','total_count':total_count})
