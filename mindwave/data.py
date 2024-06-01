from util.logger import Logger


class Data:
    def __init__(self):
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.raw_data = []
        self.attention = 0
        self.meditation = 0

        self.delta = 0
        self.theta = 0
        self.low_alpha = 0
        self.high_alpha = 0
        self.low_beta = 0
        self.high_beta = 0
        self.low_gamma = 0
        self.high_gamma = 0

    def update_data(self, **kwargs):
        for key, value in kwargs.items():
            assert hasattr(self, key), f"Invalid attribute: {key}"
            self._logger.debug(f"Updating {key} to {value}")
            setattr(self, key, value)
