import logging
import logging.config


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO

    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s'
                ' - %(name)s'
                ' - %(filename)s:%(lineno)d'
                ' - %(funcName)s() %(levelname)s'
                ' - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            }
        },
        'loggers': {
            'app': {'handlers': ['console'], 'level': level, 'propagate': False},
        },
        'root': {'handlers': ['console'], 'level': level},
    }

    logging.config.dictConfig(log_config)
