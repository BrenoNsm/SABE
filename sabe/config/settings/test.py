import os
os.environ['SECRET_KEY'] = 'test-secret-key-not-for-production'

from .development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEBUG = False
