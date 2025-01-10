## Minimal working example
A minimal example to start a functional data collection session
```python linenums="1"
from pymindwave2 import MindWaveMobile2, Session, SessionConfig

# Initialize and connect to the headset
headset = MindWaveMobile2()
success = headset.start(n_tries=5, timeout=30)

if success:  # if the headset is connected successfully
    # Create a session configuration
    sess_config = SessionConfig(
        user_name="Ahmed",
        classes=["left", "right"]  # Define your classification tasks
    )
    
    # Initialize and start the recording session
    session = Session(headset, config=sess_config)

    while headset.signal_quality != 100:
        time.sleep(1)  # wait for the user to wear the headset properly

    session.start()  # Start recording data
    
    while session.is_active:
        time.sleep(1)  # wait for the session to finish
    
    session.save()  # save the recorded data to disk
```
---
## Session Configuration attributes
```python linenums="1"
sess_config = SessionConfig(
    user_name="Ahmed",  # Name of the user
    user_age=0,         # Age of the user
    classes=["left", "right", "foot"],  # Classes used for motor imagery tasks
    n_trials=10,        # Number of trials for each class
    capture_blinks=True,  # Whether to capture blinks or not
    motor_duration=5,    # Duration of each motor imagery task in seconds
)
```
for the full list of attributes, check [SessionConfig](https://princeegy.github.io/pymindwave2/api/session/#mindwave.session.SessionConfig)
---
## Event Listeners
An example to subscribe to headset data emitted events
```python linenums="1"
from pymindwave2 import MindWaveMobile2, HeadsetDataEvent

headset = MindWaveMobile2()
success = headset.start(n_tries=5, timeout=30)

if sucess:
    def meditation_handler(event: HeadsetDataEvent):
        print(event.data.meditation)
    
    subscription = headset.on_data(meditation_handler)

    while some_condition:
        time.sleep(1)

    subscription.detach()  # Unsubscribe from the event
```
An example to reconnect to the headset if the connection is lost
```python linenums="1"
... # headset connection
def reconnect_handler(event:HeadsetStatusEvent):
    if event.status == ConnectionStatus.CONNECTION_LOST:
        headset.start(n_tries=5, timeout=30)
    
subscription = headset.on_status_change(reconnect_handler)
```

Notify user when the headset is not worn properly
```python linenums="1"
... # headset connection
def signal_quality_handler(event:SignalQualityEvent):
    if event.signal_quality < 100:
        print("Please wear the headset properly")

subscription = headset.on_signal_quality_change(signal_quality_handler)
```
---
Subscribe to session signals, such as start and end of each trial and phases of the trial. This can be used to build a GUI on top of it to create data collection environment.
```python linenums="1"
... # session and headset connection
def session_handler(event:SessionEvent):
    signal = event.signal
    if signal == SessionSignal.SESSION_START:
        print("Session started")
    elif signal == SessionSignal.TRIAL_START:
        print("Trial started for class:", event.class_name)
    elif signal == SessionSignal.REST:
        print("Resting phase")
    elif signal == SessionSignal.READY:
        print("Ready for the motor imagery task")
    elif signal == SessionSignal.CUE:
        print("Cue for the motor imagery task")
    elif signal == SessionSignal.MOTOR :
        print("Motor imagery task")
    elif signal == SessionSignal.TRIAL_END:
        print("Trial ended")
    elif signal == SessionSignal.SESSION_END:
        print("Session ended")

subscription = session.on_signal(session_handler)
```
for the full list of Session Signals, check [SessionSignal](https://princeegy.github.io/pymindwave2/api/enums/#mindwave.session.SessionSignal)

for the data collection session workflow, check [Session Workflow](https://princeegy.github.io/pymindwave2/api/session/#mindwave.session.Session)