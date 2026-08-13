import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-dovs_dc8h5u*!zdhc49e#t($1d)si&z2lv&1#8k-ef&fh1o++o"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store.apps.StoreConfig",
    "basket.apps.BasketConfig",
    "account.apps.AccountConfig",
    "order.apps.OrderConfig",
    "mptt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.categories",
                "basket.context_processors.basket",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# 配置Mysql
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ecommerce",
        "HOST": "127.0.0.1",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "root",
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "zh-Hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

USE_TZ = False

# 配置静态文件
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# 配置媒体文件夹
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 配置User模型
AUTH_USER_MODEL = "account.User"
LOGIN_REDIRECT_URL = "/account/dashboard/"
LOGIN_URL = "/account/login/"

# 配置email后端
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 配置Basket session ID
BASKET_SESSION_ID = "basket"

# 配置ALIPAY
ALIPAY_APP_ID = "9021000166675629"
ALIPAY_DEBUG = True
ALIPAY_APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "keys", "app_private_key.pem")
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "keys", "alipay_public_key.pem")

# 网关地址
ALIPAY_GATEWAY_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"

# 支付完成后的跳转地址
ALIPAY_RETURN_URL = "http://127.0.0.1:8000/order/alipay/return/"

# 推送支付结果的地址(上线时换成对应的地址)
ALIPAY_NOTIFY_URL = "http://127.0.0.1:8000/order/alipay/notify/"

# 配置debug-toolbar
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
    }
