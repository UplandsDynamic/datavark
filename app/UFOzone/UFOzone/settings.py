from pathlib import Path
from urllib.parse import urlsplit
import os, string, random, locale, logging
from .da_settings import DA_SETTINGS
from configparser import ConfigParser

logger = logging.getLogger("django")


### paths & hosts
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "UFOzone.urls"
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 30  # 30s for testing. Set to more appropriate in production
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
ALLOWED_HOSTS = ["localhost", "ufozone.co.uk"]
CORS_ORIGIN_ALLOW_ALL = True  # only set True for testing purposes
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ["http://localhost", "https://ufozone.co.uk"]
CSRF_TRUSTED_ORIGINS = ["https://*.ufozone.co.uk", "https://ufozone.co.uk"]

# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

### SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-+^w!t3^1eywb94sjhfxysxi&fm$*47ouh&kti@knfe%%-c90t5'

# # # GENERATE A NEW UNIQUE SECRET KEY (secret_key.txt) IF DOES NOT ALREADY EXIST
# # # Ensure 'secret_key' dir has been created in base directory
KEY_PATH = os.path.join(BASE_DIR, "secrets", "secret_key.txt")
try:
    with open(KEY_PATH, "r") as f:
        SECRET_KEY = f.read().strip()
except IOError:
    SECRET_KEY = "".join(
        [
            random.SystemRandom().choice(
                string.ascii_letters + string.digits + string.punctuation
            )
            for _ in range(50)
        ]
    )
    with open(KEY_PATH, "w") as f:
        f.write(SECRET_KEY)

### SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "ie", "static"),
    os.path.join(BASE_DIR),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

### application definitions
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "ie.apps.IeConfig",
    "dataview.apps.DataviewConfig",
    # 'email_service.apps.EmailServiceConfig,
    "corsheaders",
    "django_q",
    "django.contrib.gis",
    "django_tables2",
]

### Data acquisition (DA) settings
DA_SETTINGS


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
WSGI_APPLICATION = "UFOzone.wsgi.application"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # set higher than the count of fields


### middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

### templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

### databases

DB_CONFIG_PATH = os.path.join(BASE_DIR, "secrets", "db.ini")
try:
    db_config = ConfigParser()
    db_config.read(DB_CONFIG_PATH)
    db_name = db_config.get("DEFAULT", "db_name")
    db_username = db_config.get("DEFAULT", "db_username")
    db_password = db_config.get("DEFAULT", "db_password")
    db_host = db_config.get("DEFAULT", "db_host")
    db_port = db_config.get("DEFAULT", "db_port")
except Exception as e:
    logger.error(f"There was a problem with the DB configuration: {str(e)}")

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": db_name,
        "USER": db_username,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
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

### internationalisation
locale.setlocale(locale.LC_ALL, "en_GB.UTF-8")  # set locale
LANGUAGE_CODE = "en-gb"  # set language code
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = False
TIME_ZONE = "UTC"
USE_TZ = True

### django_q
Q_CLUSTER = {
    "name": "UFOzone",
    "daemonize_workers": True,
    "compress": True,
    "workers": 2,
    "recycle": 5000,
    "timeout": 99999,
    "django_redis": "django_q",
    "retry": 100000,
    "queue_limit": 4,
    "bulk": 1,
    # "orm": "default",
    "sync": 0,
    "guard_cycle": 5,
    "cpu_affinity": 1,
    "catch_up": False,
}

### caches
DEFAULT_CACHES_TTL = 0  # 0 means equates to 'do not cache'. E.g. to cache for 24 hours: ((60 * 60) * 60) * 24
CACHE_SESSION_SECONDS = 60 * 60
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = DEFAULT_CACHES_TTL  # cache session data for an hour
CACHE_MIDDLEWARE_KEY_PREFIX = "ufozone_server"
MIDDLEWARE.insert(
    0, "django.middleware.cache.UpdateCacheMiddleware"
)  # HAS TO GO FIRST IN MIDDLEWARE LIST
MIDDLEWARE.append(
    "django.middleware.cache.FetchFromCacheMiddleware"
)  # HAS TO GO LAST IN MIDDLEWARE LIST
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": DEFAULT_CACHES_TTL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "template_fragments": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": DEFAULT_CACHES_TTL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "django_q": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

### email services
EMAIL_BACKEND = ""
DEFAULT_FROM_EMAIL = ""
ANYMAIL = {
    "IGNORE_UNSUPPORTED_FEATURES": True,
}

### password validation
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

### logging
LOG_FILE = (
    "/var/log/django/ufozone.log"  # this directory & file needs to be created first!
)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
        "django_q": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
