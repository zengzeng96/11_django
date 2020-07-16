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
from django.db import transaction
from alipay import AliPay
from django.conf import settings
import os

# Create your views here.
# 配置alipay地址
private_path = os.path.join(settings.BASE_DIR, 'apps\\order\\app_private_key.pem')
public_path = os.path.join(settings.BASE_DIR, 'apps\\order\\alipay_public_key.pem')


# 获取公私钥字符串
app_private_key_string = open(private_path).read()
alipay_public_key_string = open(public_path).read()


# **********************************
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
# mysql事务操作  要么操作都失败  要么操作都成功
# 高并发事务

class OrderCommitView1(View):
    '''订单创建'''

    # 使用悲观锁
    @transaction.atomic
    def post(self, request):  # 这样的装饰之后数据库的操作就在一个事务里面了 要么都成功 要么都失败
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
        save_id = transaction.savepoint()  # 设置事务的保存点
        try:
            # todo：向df_order_info加入信息
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price
                                             )  # 因为先执行了 所以即使订单生成不成功 也会在订单信息表中添加一条记录
            # todo:用户的订单中有几个商品，需要向 df_order_goods 表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            sku_ids = sku_ids.split(',')  # [1,2]

            for sku_id in sku_ids:
                # import time
                # time.sleep(10)
                try:
                    # todo:给mysql查询操作加入悲观锁
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                    #
                except GoodsSKU.DoesNotExist:
                    transaction.savepoint_rollback(save_id)  # 事务回滚到保存点的位置
                    return JsonResponse({"res": 4, "errmsg": "商品不存在"})

                print('user:%d stock:%d' % (user.id, sku.stock))
                import time
                time.sleep(10)

                # todo:判断商品的库存

                # 从redis中获取用户索要购买的商品的数量
                count = conn.hget(cart_key, sku_id)
                if int(count) > sku.stock:
                    transaction.savepoint_rollback(save_id)  # 事务回滚到保存点的位置
                    return JsonResponse({"res": 6, "errmsg": "商品库存不足"})

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
        except Exception as e:
            transaction.rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # todo:提交事务
        transaction.savepoint_commit(save_id)

        # todo:清除用户购物车中的商品记录
        conn.hdel(cart_key, *sku_ids)  # [1,2]----->*[1,2]----->1,2   作为参数传入
        # context = {}
        return JsonResponse({'res': 5, 'message': '订单创建成功'})


class OrderCommitView(View):
    '''订单创建'''

    # 使用乐观锁
    @transaction.atomic
    def post(self, request):  # 这样的装饰之后数据库的操作就在一个事务里面了 要么都成功 要么都失败
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
        save_id = transaction.savepoint()  # 设置事务的保存点
        try:
            # todo：向df_order_info加入信息
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price
                                             )  # 因为先执行了 所以即使订单生成不成功 也会在订单信息表中添加一条记录
            # todo:用户的订单中有几个商品，需要向 df_order_goods 表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            sku_ids = sku_ids.split(',')  # [1,2]

            for sku_id in sku_ids:
                for i in range(3):
                    # import time
                    # time.sleep(10)
                    try:
                        # todo:在这里不加锁   乐观锁与悲观锁的区别
                        sku = GoodsSKU.objects.get(id=sku_id)
                        #
                    except GoodsSKU.DoesNotExist:
                        transaction.savepoint_rollback(save_id)  # 事务回滚到保存点的位置
                        return JsonResponse({"res": 4, "errmsg": "商品不存在"})

                    # print('user:%d stock:%d' % (user.id, sku.stock))
                    import time
                    time.sleep(10)

                    # todo:判断商品的库存
                    # 从redis中获取用户索要购买的商品的数量
                    count = conn.hget(cart_key, sku_id)
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(save_id)  # 事务回滚到保存点的位置
                        return JsonResponse({"res": 6, "errmsg": "商品库存不足"})

                    # todo:更新商品的库存和销量
                    origin_stock = sku.stock
                    new_stock = origin_stock - int(count)
                    new_sales = sku.sales + int(count)
                    # sku.save()
                    # update df_goods_sku set stock=new_stock,sales=new_sales where id =sku_id and stock=origin_stock
                    # 返回受影响的行数
                    print('user:%d times:%d stock:%d' % (user.id, i, sku.stock))
                    # import time
                    # time.sleep(10)
                    res = GoodsSKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                        sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_id);
                            return JsonResponse({"res": 7, "errmsg": "下单失败"})
                        continue
                    # todo：向 df_order_goods 表中加入几条记录
                    OrderGoods.objects.create(order=order,
                                              sku=sku,
                                              count=count,
                                              price=sku.price
                                              )

                    # todo:计算累加订单的总数量和总价格
                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount
                    # 跳出循环
                    break

            # todo:更新订单信息表中商品的总数量和总价格
            # total_price += transit_price
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # todo:提交事务
        transaction.savepoint_commit(save_id)

        # todo:清除用户购物车中的商品记录
        # [1,2]----->*[1,2]----->1,2   作为参数传入
        conn.hdel(cart_key, *sku_ids)
        # context = {}
        return JsonResponse({'res': 5, 'message': '订单创建成功'})


# 前端传递参数
# /order/pay
class OrderPayView(View):
    '''订单支付视图'''

    def post(self, request):
        '''订单支付'''
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')
        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        # 业务处理：使用python包调用支付宝的支付接口
        # print('进行到这里')
        alipay = AliPay(
            appid='2016102500760329',
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True  # 上线则为False  沙箱为True
        )
        # print('come here')
        # 调用接口(传参订单号和总价,标题)
        total_pay = order.total_price + order.transit_price  # Decimal类型
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(total_pay),  # 支付总金额
            subject='天天生鲜:%s' % order_id,
            return_url=None,
            notify_url=None,
        )
        # 拼接应答地址
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})

# /order/check
class CheckPayView(View):
    """查询订单是否支付成功"""
    def post(self,request):
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')
        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        # 业务处理：使用python包调用支付宝的支付接口
        print('进行到这里')
        alipay = AliPay(
            appid='2016102500760329',
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True  # 上线则为False  沙箱为True
        )
        #调用支付宝的交易查询接口
        while True:
            response=alipay.api_alipay_trade_query(order_id)#下面就是他的返回结果
            '''
            "alipay_trade_query_response": {
                "trade_no": "2017032121001004070200176844",#支付宝交易号
                "code": "10000",#接口是否调用成功
                "invoice_amount": "20.00",
                "open_id": "20880072506750308812798160715407",
                "fund_bill_list": [
                  {
                    "amount": "20.00",
                    "fund_channel": "ALIPAYACCOUNT"
                  }
                ],
                "buyer_logon_id": "csq***@sandbox.com",
                "send_pay_date": "2017-03-21 13:29:17",
                "receipt_amount": "20.00",
                "out_trade_no": "out_trade_no15",
                "buyer_pay_amount": "20.00",
                "buyer_user_id": "2088102169481075",
                "msg": "Success",
                "point_amount": "0.00",
                "trade_status": "TRADE_SUCCESS",#支付结果
                "total_amount": "20.00"
              }
            '''
            code=response.get('code')
            trade_status=response.get('trade_status')
            if code == '10000' and trade_status=='TRADE_SUCCESS':
                #支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no=trade_no
                order.order_status=4
                order.save()
                # 返回结果
                return JsonResponse({'res':3,'message':'支付成功'})
            elif code=='40004' or (code == '10000' and trade_status == 'WAIT_BUYER_PAY'):
                #等待买家付款
                # 业务处理失败 可能一会儿就会成功
                import time
                time.sleep(5)
                continue
            else:
                #支付出错
                print('*'*20,code,'   ',trade_status)
                return JsonResponse({'res':4,'message':'支付失败'})

# 订单的评论
# /order/commit/24242424322
class CommentView(LoginRequiredMixin, View):
    """订单评论"""
    def get(self, request, order_id):
        """提供评论页面"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        # 根据订单的状态获取订单的状态标题
        order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_id=order_id)
        for order_sku in order_skus:
            # 计算商品的小计
            amount = order_sku.count*order_sku.price
            # 动态给order_sku增加属性amount,保存商品小计
            order_sku.amount = amount
        # 动态给order增加属性order_skus, 保存订单商品信息
        order.order_skus = order_skus
        # 使用模板
        return render(request, "order_comment.html", {"order": order})

    def post(self, request, order_id):
        """处理评论内容"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        # 获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        # 循环获取订单中商品的评论内容
        for i in range(1, total_count + 1):
            # 获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i) # sku_1 sku_2
            # 获取评论的商品的内容
            content = request.POST.get('content_%d' % i, '') # cotent_1 content_2 content_3
            try:
                order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue

            order_goods.comment = content
            order_goods.save()

        order.order_status = 5 # 已完成
        order.save()

        return redirect(reverse("user:order", kwargs={"page": 1}))