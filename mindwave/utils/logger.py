import logging


class Logger:
    _logger = None

    @classmethod
    def configure_logger(cls, level=logging.INFO, filename="mindwave.log", filemode="w"):
        cls._logger = logging.getLogger()
        st_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(filename, mode=filemode)
        f_handler.setLevel(level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s::%(name)s.%(funcName)s - %(message)s")
        f_handler.setFormatter(formatter)
        st_handler.setFormatter(formatter)
        cls._logger.addHandler(st_handler)
        cls._logger.addHandler(f_handler)
        cls._logger.setLevel(level)

    @classmethod
    def get_logger(cls, name):
        if cls._logger is None:
            cls.configure_logger()
        return cls._logger.getChild(name)
