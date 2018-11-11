'''
    Raspberry PI POV Display
    Braden Mars
'''

import os
from time import sleep

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient as AWSClient
from gpiozero import Motor
from gpiozero.pins.pigpio import PiGPIOFactory


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


# AWS/MQTT Definitions
profile = {
    'host': os.environ.get('AWS_HOST'),
    'port': 443,
    'rootCert': os.environ.get('ROOT_CERT'),
    'clientID': 'POVPiMain',
    'topics': {
        'display': 'povRPi/display'
    },
    'rpi_host': os.environ.get('RPI')
}


# AWS Client Setup
client = AWSClient(profile['clientID'], useWebsocket=True)
client.configureEndpoint(profile['host'], 443)
client.configureCredentials(profile['rootCert'])

# AWSIoTMQTTClient connection configuration
client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec
client.connect()

# Subscribe
topics = profile['topics']
client.subscribe(topics['display'], 0, customCallback)
print("Subscribed to aws topic")
sleep(2)


factory = PiGPIOFactory(host=profile['rpi_host'])

motor = Motor(forward=17, backward=18, pin_factory=factory)

while 1:
    motor.forward()
    print('Motor going forward...')
    sleep(5)
    print('Motor stopping...')
    motor.stop()
    sleep(5)
