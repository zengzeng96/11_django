from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from user.models import Address
from utils.mixin import LoginRequiredMixin
from django.http import JsonResponse
from order.models import OrderInfo, OrderGoods
from datetime import datetime


# Create your views here.

# /order/place
class OrderPlaceView(LoginRequiredMixin, View):
    """订单提交页面显示"""

    def post(self, request):
        '''提交订单页面显示'''
        # 获取登录的用户
        user = request.user
        # 获取参数  sku_ids
        sku_ids = request.POST.getlist('sku_ids')
        # 校验参数
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('cart:show'))
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 遍历sku_ids获取用户要购买的商品的信息
        skus = []
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户所要购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku增加属性 count 保存购买数量
            sku.count = count
            # 动态给sku增加属性 amount 保存每种商品的小计
            sku.amount = amount
            skus.append(sku)
            # 累加计算商品的总件数和总价格
            total_count += int(count)
            total_price += amount
        # 运费：实际开发的时候属于一个子系统
        transit_price = 10  # 我们在这里没做 直接给他写死
        # 实付款
        total_pay = total_price + transit_price
        # 获取用户的收件地址
        addrs = Address.objects.filter(user=user)
        # 组织上下文
        sku_ids = ','.join(sku_ids)  # [1,25]---->1,25
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }
        # 使用模版
        return render(request, 'place_order.html', context)


# 用户点击提交订单 ：收货地址 addr_id  支付方式pay_method   商品的id(sku_ids)
class OrderCommitView(View):
    '''订单创建'''

    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errmsg": "用户未登陆"})
        # 接受参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({"res": 1, "errmsg": "参数不完整"})

        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({"res": 2, "errmsg": "非法的支付方式"})
        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            # 地址不存在
            return JsonResponse({"res": 3, "errmsg": "地址非法"})
        # todo:创建订单的核心业务

        # 组织参数
        # 订单id: 202007014223145+用户id     日期时间+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费
        transit_price = 10  # 写死

        # 总数目和总金额
        total_count = 0
        total_price = 0
        # todo：向df_order_info加入信息
        order = OrderInfo.objects.create(order_id=order_id,
                                         user=user,
                                         addr=addr,
                                         pay_method=pay_method,
                                         total_count=total_count,
                                         total_price=total_price,
                                         transit_price=transit_price
                                         )
        # todo:用户的订单中有几个商品，需要向 df_order_goods 表中加入几条记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        sku_ids = sku_ids.split(',')  # [1,2]

        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                return JsonResponse({"res": 4, "errmsg": "商品不存在"})

            # 从redis中获取用户索要购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            # todo：向 df_order_goods 表中加入几条记录
            OrderGoods.objects.create(order=order,
                                      sku=sku,
                                      count=count,
                                      price=sku.price
                                      )
            # todo:更新商品的库存和销量
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()
            # todo:计算累加订单的总数量和总价格
            amount = sku.price * int(count)
            total_count += int(count)
            total_price += amount
        # todo:更新订单信息表中商品的总数量和总价格
        # total_price += transit_price
        order.total_count = total_count
        order.total_price = total_price
        order.save()
        # todo:清除用户购物车中的商品记录
        conn.hdel(cart_key, *sku_ids)#[1,2]----->*[1,2]----->1,2   作为参数传入
        # context = {}
        return JsonResponse({'res':5,'message':'订单创建成功'})
