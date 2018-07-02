import os
import logging

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
            'format': '%(asctime)s %(message)s',
            'datefmt': '[%d/%m/%Y %H:%M:%S %z]'
        }
    }
}
