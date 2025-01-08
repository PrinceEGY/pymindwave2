<!-- Intro -->
# PyMindWave2


A Python package that simplifies connecting and gathering data from the [Neurosky MindWave Mobile 2](https://store.neurosky.com/pages/mindwave) EEG headset.

This package is made to ease the process of data collection and interfacing with the **MindWave Mobile 2** EEG headset mainly for researchers and students who are interested in using the headset for their projects.

<u>**Note:** This is an unofficial package and is not affiliated with [Neurosky](https://neurosky.com/).</u>

<!-- Features -->
## Features

- **Easy to use**: Provides a simple and intuitive API to interact with the headset.
- **Data collection**: Provides a way to manage data collection sessions with different configurations.
- **Event-driven**: Allows you to register callbacks for different events to ease the process of handling data.
- **Built-in retry and timeout**: Automatically retries to connect to the headset if the connection fails.
- **Fully documented**: You don't know what a function does? Just check the documentation.

<!-- Installation -->
## Installation

**Prerequisites: Before installing the package, make sure to do the following:**

-  Install the official NeuroSky [ThinkGear Connector](http://support.neurosky.com/kb/applications/what-is-the-thinkgear-connector-and-why-do-i-need-it) software on your computer. It enables communication between your computer and the headset through a serial port.
You can download it from [here](https://download.neurosky.com/public/Products/Utility/TGC/). And make sure it's running in the background.

-  Pair the headset with your computer via Bluetooth. You can follow the instructions in [NeuroSky's pairing guide](http://support.neurosky.com/kb/mindwave-mobile-2/cant-pair-mindwave-mobile-2-with-computer-or-mobile-device).

Then you can install the package using pip:

```bash
pip install pymindwave2
```

<!-- Usage -->
## Quick Start


A minimal example to start a data collection session:
```py
from pymindwave2 import MindWaveMobile2, Session, SessionConfig

# Initialize and connect to the headset
headset = MindWaveMobile2()
success = headset.start(n_tries=5, timeout=30)

if success:  # if the headset is connected successfully
    # Create a session configuration
    sess_config = SessionConfig(
        user_name="Ahmed",
        ...  # other configurations
        classes=["left", "right"]
    )
    
    # Initialize and start the recording session
    session = Session(headset, config=sess_config)
    session.start()  # Start recording data
    
    while session.is_active:
        pass  # wait for the session to finish
    
    session.save()  # save the recorded data to disk
```

for more examples and detailed usage, check the [Examples](https://princeegy.github.io/pymindwave2/examples)

<!-- Contributing -->
## Contributing
Feel free to contribute to this package to add, update, fix, and suggest other features.


