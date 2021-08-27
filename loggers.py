#! /usr/bin/env python3
import logging.config
import os
import shutil

"""
Log settings
"""


logger_config = {
    'version': 1,
    'formatters': {
        'formatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'info_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'formatter',
            'filename': 'info_log.log',
            'encoding': 'UTF-8',
            'delay': 'True'
        },
        'error_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'formatter',
            'filename': 'error_log.log',
            'encoding': 'UTF-8',
            'delay': 'True'
        }
    },
    'loggers': {
        'info_log': {
            'handlers': ['info_handler'],
            'level': 'INFO',
        },
        'error_log': {
            'handlers': ['error_handler'],
            'level': 'ERROR'
        }
    },
}

logging.config.dictConfig(config=logger_config)
info_log = logging.getLogger(name='info_log')
error_log = logging.getLogger(name='error_log')


if __name__ == '__main__':
    info_log.info('TEST')
    error_log.exception('TEST')
