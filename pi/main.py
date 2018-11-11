'''
    main.py
    Persistence-Of-Vision Raspberry Pi (POVPi)
    Raspberry Pi Controller
    
'''

import json
import os
from pprint import pprint
from signal import pause
from time import sleep

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient as AWSClient
from gpiozero import Motor
from gpiozero.pins.pigpio import PiGPIOFactory

from alpha import display


def create_aws_client(profile):
    """create and connect AWS MQTT Client"""
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
    return client


def update_state(client, userdata, message):
    """update state on shadow update event"""
    msg = message.payload.decode("utf-8")
    payload = json.loads(msg)
    state.update(payload['state']['desired'])
    print('new state')
    pprint(state)
    return state


def break_display(sentence):
    """interrupts current display if state is updated"""
    if sentence != state['display'] or not state['enabled']:
        print("State update detected, breaking sentence...")
        return True
    return False


def main(client):
    """Main POVPi Event Loop"""
    # Subscribe to AWS Updates
    client.subscribe('$aws/things/POVRPi/shadow/update/accepted',
                     0, update_state)
    print("Subscribed to aws topic")
    sleep(2)
    while 1:
        while state['enabled']:
            display(state['display'], interrupt=break_display)


if __name__ == '__main__':
    """POVPi Entry Point"""
    # AWS/MQTT Definitions
    profile = {
        'host': os.environ.get('AWS_HOST'),
        'port': 443,
        'rootCert': os.environ.get('ROOT_CERT'),
        'clientID': 'POVPiMain',
        'rpi_host': os.environ.get('RPI')
    }
    # Local State
    state = {
        'enabled': False,
        'display': 'Hello World'
    }
    # Create MQTT Broker Client
    client = create_aws_client(profile)
    # GPIO Remote Access
    factory = PiGPIOFactory(host=profile['rpi_host'])
    # DC Motor
    motor = Motor(forward=17, backward=18, pin_factory=factory)
    main(client)
    pause()
