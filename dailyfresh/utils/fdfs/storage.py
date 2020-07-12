from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client,get_tracker_conf
from django.conf import settings

class FDFSStorage(Storage):
    def __init__(self,client_conf=None,base_url=None):
        if client_conf is None:
            client_conf=settings.FDFS_CLIENT_CONF
        self.client_conf=client_conf
        if base_url is None:
            base_url=settings.FDFS_URL
        self.base_url=base_url

    """fastdfs文件存储类"""
    def open(self, name, mode):
        pass
    def save(self, name, content):
        '''保存文件时使用'''
        # name 选择的上传文件的名字
        # content :包含你上传文件内容的File对象
        # 创建一个fdfs_client对象
        tracker=get_tracker_conf(self.client_conf)
        client=Fdfs_client(tracker)
        # 上传文件到fdfs系统中
        ret=client.upload_by_buffer(content.read())
        # dict {
        #     'Group name'      : group_name,
        #     'Remote file_id'  : remote_file_id,#
        #     'Status'          : 'Upload successed.',#
        #     'Local file name' : '',
        #     'Uploaded size'   : upload_size,
        #     'Storage IP'      : storage_ip
        # }
        # 上面的就是返回的格式
        if not ret.get('Status')=='Upload successed.':
            # 上传失败
            raise Exception('上传文件到fdfs失败')
        # 获取返回的文件id
        file_name=ret.get('Remote file_id')
        return file_name
    def exists(self, name) :
        # django判断文件名是否可用
        return False

    def url(self,name):
        '''Django 返回访问url的路径'''
        return self.base_url+name
