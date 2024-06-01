import logging


class Logger:
    _instance = None

    def __new__(cls, level=logging.DEBUG, filename=None, filemode="w"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._configure_logger(level, filename, filemode)
        return cls._instance

    def _configure_logger(self, level, filename, filemode):
        self.logger = logging.getLogger()
        st_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(filename, mode=filemode)
        f_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(levelname)s:%(asctime)s %(name)s: %(message)s", datefmt="%H:%M:%S"
        )
        f_handler.setFormatter(formatter)
        st_handler.setFormatter(formatter)
        self.logger.addHandler(st_handler)
        self.logger.addHandler(f_handler)
        self.logger.setLevel(level)

    def get_logger(self, name):
        return self.logger.getChild(name)
