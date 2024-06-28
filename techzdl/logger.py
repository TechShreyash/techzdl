import logging


class Logger:
    def __init__(self, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

        # StreamHandler for console output
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
