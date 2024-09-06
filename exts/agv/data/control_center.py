from paho.mqtt import client as mqtt_client

class MQTTClient:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.client = None

    def on_message(self, client, userdata, message):
        payload = message.payload.decode()
        if payload == "stop_conveyor":
            self.db.internal_state.stop_conveyor_flag = True
        elif payload == "activate_conveyor":
            self.db.internal_state.activate_conveyor_flag = True

    def start(self):
        self.client = mqtt_client.Client()
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port)
        self.client.subscribe("conveyor/commands")
        self.client.loop_start()

    def stop(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

def setup(db: og.Database):
    state = db.internal_state

    state.mqtt_flag = False
    state.mqtt_client = None
    
    state.stop_conveyor_flag = False
    state.activate_conveyor_flag = False

    # Initialize MQTT client
    state.mqtt_host = '127.0.0.1'  # Set your MQTT broker host
    state.mqtt_port = 1883  # Set your MQTT broker port

def cleanup(db: og.Database):
    if db.internal_state.mqtt_client:
        db.internal_state.mqtt_client.stop()

def compute(db: og.Database):
    state = db.internal_state

    if not state.mqtt_flag:
        state.mqtt_flag = True
        state.mqtt_client = MQTTClient(state.mqtt_host, state.mqtt_port, db)
        state.mqtt_client.start()

    if state.stop_conveyor_flag:
        db.outputs.is_stop = True
        state.stop_conveyor_flag = False
    else:
        db.outputs.is_stop = False

    if state.activate_conveyor_flag:
        db.outputs.is_activate = True
        state.activate_conveyor_flag = False
    else:
        db.outputs.is_activate = False

    return True
