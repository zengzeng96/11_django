from django.db import models

# Create your models here.


class AreaInfo(models.Model):
    '''地址模型类'''
    atitle = models.CharField(verbose_name='标题', max_length=20)
    # verbose_name  后台管理时显示的字段标题
    # 自关联属性
    aParent = models.ForeignKey('self', null=True, blank=True)
    # blank=True  后台允许为空

    def __str__(self):  # 后台显式不再显式AreaInfo objects
        # 而是显式每个对象的atitle属性
        return self.atitle

    def title(self):  # 写的一个方法 可以在模型管理类中被调用
        return self.atitle
    title.admin_order_field = 'atitle'  # 函数指定返回的数据也可以通过单击最上面的标题栏进行排序
    # 没有上面这一行函数定义的数据就不能进行点击排序
    
    title.short_description = '地区名称'  # 指定函数定义返回的数据字段标题的名称

    def parent(self):
        '''返回当前地区的父级地区'''
        if self.aParent is None:  # 省级地区没有父级地区
            return ''
        return self.aParent.atitle
    parent.short_description = '父级地区名称'


class PicTest(models.Model):
    """后台上传图片类"""
    goods_pic = models.ImageField(upload_to='booktest')
    # upload_to指定图片上传到哪个目录下，这个目录是相对于media文件夹的
    # 这个目录是相对于media文件夹的
