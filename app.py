import logging
from util.logger import Logger

from mindwave.headset import MindWaveMobile2

Logger(level=logging.DEBUG, filename="mindwave.log", filemode="w")
headset = MindWaveMobile2()
headset.connect(n_tries=3, timeout=20)
while True:
    pass
