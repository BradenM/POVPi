# POVPi

A Fancy AWS enabled Persistence of Vision display controlled by a Raspberry Pi

## Raspberry Pi

Any Code that goes on the Raspberry Pi is located under the [**Pi**](https://github.com/BradenM/POVPi/tree/master/pi) folder.

Basically sets up an MQTT client to AWS IoT and watches for any external updates to its device shadow and acts accordingly.

## Web Interface

Web interface code is under the [**Web**](https://github.com/BradenM/POVPi/tree/master/web) folder.

Just a simple Flask server hosted on AWS Lambda & API Gateway with [Zappa](https://github.com/Miserlou/Zappa).

Current lets you remotely turn on/off the POVPi and change/view the text it is displaying.
