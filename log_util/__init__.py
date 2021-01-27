import logging

_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
_DATE_FORMAT = "%m-%d-%Y %H:%M:%S %p"  # 日期格式
_fp = logging.FileHandler('blog.log', encoding='utf-8')
_fs = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT, datefmt=_DATE_FORMAT, handlers=[_fp, _fs])  # 调用
log = logging.getLogger()
