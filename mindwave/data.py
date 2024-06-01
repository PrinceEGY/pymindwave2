from util.logger import Logger


class Data:
    def __init__(self):
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.raw_data = [0] * 512
        self.attention = 0
        self.meditation = 0

        self.delta = 0
        self.theta = 0
        self.lowAlpha = 0
        self.highAlpha = 0
        self.lowBeta = 0
        self.highBeta = 0
        self.lowGamma = 0
        self.highGamma = 0

    def update_data(self, **kwargs):
        for key, value in kwargs.items():
            assert hasattr(self, key), f"Invalid attribute: {key}"
            self._logger.debug(f"Updating {key} to {value}")
            setattr(self, key, value)
