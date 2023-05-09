"""
日志文件配置
"""
from logging import config
import logging
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,		# 不使其他日志失效
    'formatters': {		# 日志格式化器
        'default': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s %(levelname)s %(message)s',
        },
    },
    'handlers': {		# 日志处理器
        'console': {		# 标准输出输出
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file': {		# 输出到文件
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 所使用的处理类，这个类可以固定时间开始新的日志，保存原来的日志
            'formatter': 'default',
            'when': "d",  # 时间单位可以是h, d, m , y
            'interval': 1,		# 单位数量，多长时间开始新的记录
            'backupCount': 30,		# 能保存的最大日志文件数量
            'filename': 'output.log',
            'encoding': 'utf-8'
        }
    },
    'loggers': {		# 日志记录器
        'StreamLogger': {
            'handlers': ['console'],	# 所使用的处理器
            'level': 'DEBUG',
        },
        'FileLogger': {
            # 既有 console Handler，还有 file Handler
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }
}
# 加载配置
config.dictConfig(logging_config)
# 实例化logger 加载loggers的配置
logger = logging.getLogger("FileLogger")
