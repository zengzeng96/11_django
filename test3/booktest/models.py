from django.db import models

# Create your models here.
class AreaInfo(models.Model):
    '''地址模型类'''
    atitle=models.CharField(verbose_name='标题',max_length=20)
    # 自关联属性
    aParent=models.ForeignKey('self',null=True,blank=True)
    # blank=True  后台允许为空

    def __str__(self):
        return self.atitle

    def title(self):
        return self.atitle
    title.admin_order_field='atitle'#函数指定返回的数据也可以进行排序
    #但是必须写这一句代码

    title.short_description='地区名称'

    def parent(self):
        '''返回当前地区的父级地区'''
        if self.aParent is None:#省级地区没有父级地区
            return ''
        return self.aParent.atitle
    parent.short_description='父级地区名称'
    

class PicTest(models.Model):
    """后台上传图片类"""
    goods_pic=models.ImageField(upload_to='booktest')
    #这个目录是相对于media文件夹的
    
        