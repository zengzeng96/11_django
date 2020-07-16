from alipay import AliPay
import os

# Create your views here.
# 配置alipay地址
private_path = os.path.join(os.getcwd(), 'apps\\order\\app_private_key.pem')
public_path = os.path.join(os.getcwd(), 'apps\\order\\alipay_public_key.pem')
print(private_path)
print(public_path)

# 获取公私钥字符串
app_private_key_string = open(private_path).read()
alipay_public_key_string = open(public_path).read()



alipay = AliPay(
            appid='2016102500760329',
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True  # 上线则为False  沙箱为True
        )
print(id(alipay))