from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel
# Create your models here.


class User(AbstractUser, BaseModel):
    '''用户模型类'''
    # 继承自该类 AbstractUser  
    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class AddressManager(models.Manager):
    """地址模型管理器类"""
    # self.model获取self对象所在的模型类
    # 1.改变原有的数据查询集
    # 2.用于操作模型类的数据方法
    def get_default_address(self,user):
        '''获取用户的默认收货地址'''
        try:
            address=self.get(user=user,is_default=True)
        except self.model.DoesNotExist:
            #说明不存在默认收货地址
            address=None
        return address
        #调用方法 Addess.objects.get_default_address(user)
    

    
class Address(BaseModel):
    '''地址模型类'''
    user = models.ForeignKey('User', verbose_name='所属账户')#外键
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    objects=AddressManager()

    class Meta:
        db_table = 'df_address'#数据库表名
        verbose_name = '地址'#后台管理的时候的名字
        verbose_name_plural = verbose_name#去掉后台管理时名字后面的s

