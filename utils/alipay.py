from alipay import AliPay
from django.conf import settings


def get_alipay_client():
    """初始化并返回Alipay实例"""

    with open(settings.ALIPAY_APP_PRIVATE_KEY_PATH, "r") as f:
        app_pricate_key_string = f.read()
    with open(settings.ALIPAY_PUBLIC_KEY_PATH, "r") as f:
        alipay_public_key_string = f.read()

    alipay = AliPay(
        appid=settings.ALIPAY_APP_ID,
        app_notify_url=settings.ALIPAY_NOTIFY_URL,
        app_private_key_string=app_pricate_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=settings.ALIPAY_DEBUG,
    )

    return alipay
