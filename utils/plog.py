# !/usr/bin/env python
# -*- coding: utf-8 -*-

class PrettyLogger:
    """打印漂亮的日志类"""

    def __init__(self, logger):
        self.logger = logger
        self.steps = 0  # 步骤数

    def http_log(self, http_data, level="info"):
        """
        打印http请求日志信息
        @param http_data: 经过协议类中，http_data_analyze函数处理过的返回值
        @param level: 打印日志等级，默认info
                        e.g. debug、info、warning、warn、info、error、exception、critical

        @return:
        """

        url = http_data['url']
        req = http_data['req']
        res = http_data['res']

        getattr(self.logger, level)(f"【 url  】-【{url}】\n【 请求 】\n{req}\n【 响应 】\n{res}\n\n\n\n")

    def step_info(self, msg, *args, **kwargs):
        self.steps += 1
        msg = f'【step {self.steps}】-【{msg}】'
        self.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warn(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
