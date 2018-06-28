import os
import logging
import pytz

timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Bangkok'))

log_setting = {
    'version': 1,
    'handlers': {
        'console-info': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        },
        'console-error': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'stream': 'ext://sys.stderr'
        }
    },
    'loggers': {
        'aiohttp.access.custom': {
            'level': 'INFO',
            'handlers': ['console-info']
        },
        'aiohttp.client': {
            'level': 'INFO',
            'handlers': ['console-info'],
        },
        'aiohttp.server': {
            'level': 'ERROR',
            'handlers': ['console-error'],
        }
    },
    'formatters': {
       'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
       }
    }
}
