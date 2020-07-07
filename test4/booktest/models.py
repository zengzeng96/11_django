from django.db import models

# Create your models here.
class BookInfo(models.Model):
    '''图书模型类'''
    # 图书名称
    btitle = models.CharField(max_length=20, db_column='title')
    # 图书价格  最大位数为10   小数位数为2
    # bprice=models.DecimalField(max_digits=10,decimal_places=2)#设置小数点的位数为2
    # 出版日期
    bpub_date = models.DateField()
    # 阅读数量
    bread = models.IntegerField(default=0)
    # 评论数量
    bcomment = models.IntegerField(default=0)
    # 逻辑删除  删除标记   不对数据库的值做真正的删除  删除的话该改为 True
    isDelete = models.BooleanField(default=False)

    # book=models.Manager()#自定义一个Manager类对象  没有什么卵用
    # objects = BookInfoManager()
    class Meta:
        db_table='bookinfo'