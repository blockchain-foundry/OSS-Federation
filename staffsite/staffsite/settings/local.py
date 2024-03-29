from .dev import *

CHART_API_URL = "http://140.112.29.201:5566/api/v1"
STATISTICS_API_URL = CHART_API_URL


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_staffsite',
        'USER': 'oss_alliance',
        'PASSWORD': 'oss_alliance',
        'HOST': 'localhost',
        'PORT': '',
    },
    'website': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_website',
        'USER': 'oss_alliance',
        'PASSWORD': 'oss_alliance',
        'HOST': 'localhost',
        'PORT': '',
     },
    'chart_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chart',
        'USER': 'oss_alliance',
        'PASSWORD': 'oss_alliance',
    }
}
