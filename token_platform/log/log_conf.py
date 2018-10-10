import logging

log_setting = {
    'version': 1,
    'handlers': {
        'console-info': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
        },
        'console-error': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'stream': 'ext://sys.stderr',
            'formatter': 'default',
        },
        'file-info': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'filename': '/opt/access.log',
            'formatter': 'default',
        },
        'file-error': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'filename': '/opt/error.log',
            'formatter': 'default',
        },
        'audit-file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/audit_log.log',
            'maxBytes': 10485760,  # 10MB
            'formatter': 'audit',
        },
    },
    'loggers': {
        'aiohttp.access.custom': {'level': 'INFO', 'handlers': ['console-info', 'file-info']},
        'aiohttp.client': {'level': 'INFO', 'handlers': ['console-info']},
        'aiohttp.server': {'level': 'ERROR', 'handlers': ['console-error', 'file-error']},
        'audit': {'level': 'INFO', 'handlers': ['audit-file']},
    },
    'formatters': {
        'default': {'format': '%(asctime)s %(message)s', 'datefmt': '[%d/%m/%Y %H:%M:%S %z]'},
        'audit': {'format': '%(asctime)s %(levelname)s %(message)s'},
    },
}
