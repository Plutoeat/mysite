"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from utils.get_env import get_env_bool, get_env_value

# 加载环境变量
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_value('DJANGO_SECRET_KEY', 'django-insecure-u^#h%k1naj^*-ma!2(j6^-p0x20ip=85c^+i!%mbjmvbckn-qs')
SECURE_HSTS_SECONDS = 0
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_bool('DJANGO_DEBUG', True)
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://example.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # 博客模块必须引用 mdeditor - md 编辑器; haystack - 搜索引擎
    'mdeditor',
    'haystack',
    'blog',
    'accounts',
    'websys',
    'comments',
    'compressor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'blog.middleware.OnlineMiddleware'
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.seo_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    # 配置缓存
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "TIMEOUT": 60 * 60 * 3,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': get_env_value('MYSQL_DATABASE', 'testDb'),
            'USER': get_env_value('MYSQL_USER_NAME', 'testUser'),
            'PASSWORD': get_env_value('MYSQL_PASSWORD', '123456'),
            'HOST': get_env_value('MYSQL_HOST', 'localhost'),
            'PORT': int(get_env_value('MYSQL_PORT', '3306')),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'DATABASE': 0,
            'TIMEOUT': 60 * 60 * 3,
            'LOCATION': f'redis://{get_env_value("REDIS_URL", "localhost:6379")}',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = "/var/www/static"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 邮箱配置
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = get_env_value('EMAIL_HOST', 'smtp.mxhichina.com')
EMAIL_PORT = int(get_env_value('EMAIL_PORT', 465))
EMAIL_USE_SSL = get_env_bool('EMAIL_USE_SSL', True)
EMAIL_USE_TLS = get_env_bool('EMAIL_USE_TLS', False)
EMAIL_HOST_USER = get_env_value('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = get_env_value('EMAIL_HOST_PASSWORD', None)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMINS = [('admin', get_env_value('ADMIN_EMAIL', 'admin@admin.com'))]

# log 配置
LOG_PATH = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'log_file'],
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}.{funcName}:{lineno:d} {module}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} [{lineno:d} {module}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'mysite.log',
            'when': 'D',
            'formatter': 'verbose',
            'interval': 1,
            'delay': True,
            'backupCount': 5,
            'encoding': 'utf-8'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'mysite': {
            'handlers': ['log_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

# 密码哈希方式
PASSWORD_HASHERS = ["django.contrib.auth.hashers.BCryptPasswordHasher", ]

# 启用站点框架
SITE_ID = 1

# 配置媒体文件
MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_ROOT = '/var/www/media'

# DJANGO-COMPRESSOR 配置
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other compressor 压缩文件
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    # creates absolute urls from relative ones
    'compressor.filters.css_default.CssAbsoluteFilter',
    # css minimizer
    'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

# 时间格式化配置
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

# 配置 markdown 工具
X_FRAME_OPTIONS = 'SAMEORIGIN'
CSP_DEFAULT_SRC = ("'self'",)

MDEDITOR_CONFIGS = {
    'default': {
        'width': '80%',  # Custom edit box width
        'height': 500,  # Custom edit box height
        'toolbar': ["undo", "redo", "|",
                    "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                    "h1", "h2", "h3", "h5", "h6", "|",
                    "list-ul", "list-ol", "hr", "|",
                    "link", "reference-link", "image", "code", "preformatted-text", "code-block", "table", "datetime",
                    "emoji", "html-entities", "pagebreak", "goto-line", "|",
                    "help", "info",
                    "||", "preview", "watch", "fullscreen"],  # custom edit box toolbar
        'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],  # image upload format type
        'image_folder': 'editor',  # image save the folder name
        'theme': 'default',  # edit box theme, dark / default
        'preview_theme': 'default',  # Preview area theme, dark / default
        'editor_theme': 'default',  # edit area theme, pastel-on-dark / default
        'toolbar_autofixed': True,  # Whether the toolbar capitals
        'search_replace': True,  # Whether to open the search for replacement
        'emoji': True,  # whether to open the expression function
        'tex': True,  # whether to open the tex chart function
        'flow_chart': True,  # whether to open the flow chart function
        'sequence': True,  # Whether to open the sequence diagram function
        'watch': True,  # Live preview
        'lineWrapping': False,  # lineWrapping
        'lineNumbers': False,  # lineNumbers
        'language': 'zh'  # zh / en / es
    }
}

# 模块配置
# accounts 配置
AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = ['backends.authentication_backend.AuthModelBackend']
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = '/'

# blog 配置
# haystack 配置

if get_env_value('ELASTICSEARCH_USER', False) and get_env_value('ELASTICSEARCH_PASSWORD', False) and get_env_value(
        'ELASTICSEARCH_CA', False):
    scheme = 'https'
    security = True
else:
    scheme = 'http'
    security = False
if get_env_value('ELASTICSEARCH_HOST', False) and get_env_value('ELASTICSEARCH_PORT', False):
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'backends.elasticsearch_backend.ElasticSearchEngine',
            'URL': scheme + '://' + get_env_value('ELASTICSEARCH_HOST', 'localhost') + ':' + get_env_value(
                'ELASTICSEARCH_PORT', '9200') + '/',
            'INDEX_NAME': 'blog_index',
        },
    }
    if security:
        HAYSTACK_CONNECTIONS['default']['KWARGS'] = {
            'http_auth': (
                get_env_value('ELASTICSEARCH_USER', 'elastic'), get_env_value('ELASTICSEARCH_PASSWORD', '123456')),
        }

    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': [{
                'scheme': scheme,
                'host': get_env_value('ELASTICSEARCH_HOST', 'localhost'),
                'port': int(get_env_value('ELASTICSEARCH_PORT', 9200)),
            }],
            'timeout': 30
        },
        'security': security,
        'username': get_env_value('ELASTICSEARCH_USER', 'elastic'),
        'password': get_env_value('ELASTICSEARCH_PASSWORD', '123456'),
        'ca_certs': get_env_value('ELASTICSEARCH_CA', '/etc/elasticsearch/certs/http_ca.crt')
    }
else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'backends.whoosh_cn_backend.WhooshEngine',
            'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
            'INDEX_NAME': 'blog_index'
        }
    }

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
