import logging
from mindwave.data import Data
from util.event_handler import EventType
from util.logger import Logger

from mindwave.headset import MindWaveMobile2

Logger(level=logging.DEBUG, filename="mindwave.log", filemode="w")
headset = MindWaveMobile2()
headset.connect(n_tries=3, timeout=20)


headset.add_listener(event_type=EventType.HeadsetData, listener=print)
while True:
    pass
