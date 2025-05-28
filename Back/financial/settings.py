# Back/financial/settings.py
from pathlib import Path
import mimetypes
from dotenv import load_dotenv
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

###################### 금융감독원 API ######################
FSS_API_KEY = os.getenv('FSS_API_KEY')
###########################################################

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u$8$*vbj5bk^imba043t@vyic3x)g9f&3()2=(p$tji0n-j&np'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    # 프로젝트 앱
    'accounts',
    'financial_products',
    'simulator',
    'insight',
    'strategies',
    'marketplace',
    'community',
    'commodities',
    'bank_locations',
    'notifications',
    #####################

    # 서드파티
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'debug_toolbar',

    # 기본 Django
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


MIDDLEWARE = [
    ###
    'corsheaders.middleware.CorsMiddleware', # CORS
    ###
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ###
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # Vue 개발 서버 주소 (실제 사용하는 포트로 변경)
    "http://127.0.0.1:5173", # Vue 개발 서버 주소 (실제 사용하는 포트로 변경)
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'financial.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'financial.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

# 디버그 툴바 때문에 추가함
mimetypes.add_type("application/javascript", ".js", True)


##########
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}



# CORS
CORS_ALLOW_ALL_ORIGINS = True

# 구글 OAuth2 설정
GOOGLE_CLIENT_ID = '63305261515-pi4ctd8uadq4g5h99vp06em372f054c2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:8000/auth/google/callback/'


# 카카오 OAuth2 설정
KAKAO_REST_API_KEY = '33f3ec94f777f53d0562551623051ee3'
KAKAO_REDIRECT_URI = 'http://127.0.0.1:8000/auth/kakao/callback/'



###############
USE_CELERY = os.getenv("USE_CELERY", "false").lower() == "true"
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
