import logging


class Logger:
    _instance = None

    def __new__(cls, level=logging.DEBUG, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
            cls._instance._configure_logger(level)
        return cls._instance

    def _configure_logger(self, level):
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(levelname)s:%(asctime)s %(name)s: %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def get_logger(self, name):
        return self.logger.getChild(name)
