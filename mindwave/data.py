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
            setattr(self, key, value)

    def __repr__(self) -> str:
        raw_summary = (
            ", ".join(map(str, self.raw_data[:5]))
            + "...."
            + ", ".join(map(str, self.raw_data[-5:]))
            + f" (length: {len(self.raw_data)})"
        )
        return (
            f"Data(raw_data={raw_summary}, attention={self.attention}, "
            f"meditation={self.meditation}, delta={self.delta}, theta={self.theta}, "
            f"lowAlpha={self.lowAlpha}, highAlpha={self.highAlpha}, lowBeta={self.lowBeta}, "
            f"highBeta={self.highBeta}, lowGamma={self.lowGamma}, highGamma={self.highGamma})"
        )
