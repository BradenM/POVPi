'''
    Raspberry PI POV Display
    Braden Mars
'''

import json
import os
from pprint import pprint
from time import sleep

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient as AWSClient
from gpiozero import Motor
from gpiozero.pins.pigpio import PiGPIOFactory

# AWS/MQTT Definitions
profile = {
    'host': os.environ.get('AWS_HOST'),
    'port': 443,
    'rootCert': os.environ.get('ROOT_CERT'),
    'clientID': 'POVPiMain',
    'rpi_host': os.environ.get('RPI')
}


# AWS Client Setup
client = AWSClient(profile['clientID'], useWebsocket=True)
client.configureEndpoint(profile['host'], 443)
client.configureCredentials(profile['rootCert'])

# AWSIoTMQTTClient connection configuration
client.configureAutoReconnectBackoffTime(1, 32, 20)
# Infinite offline Publish queueing
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)  # Draining: 2 Hz
# Connect
client.connect()


# State Manage
state = {
    'enabled': False,
    'display': 'Hello World'
}


def update_state(client, userdata, message):
    """update state on shadow update event"""
    msg = message.payload.decode("utf-8")
    payload = json.loads(msg)
    state.update(payload['state']['desired'])
    print('new state')
    pprint(state)
    return state


# Subscribe
pprint('OG STATE: %s' % state)
client.subscribe('$aws/things/POVRPi/shadow/update/accepted',
                 0, update_state)
print("Subscribed to aws topic")
sleep(2)


factory = PiGPIOFactory(host=profile['rpi_host'])

motor = Motor(forward=17, backward=18, pin_factory=factory)

while 1:
    if(state['enabled'] == True):
        print('Motor going forward...')
        motor.forward()
        sleep(2)
    else:
        print('Motor stopped')
        motor.stop()
        sleep(2)
