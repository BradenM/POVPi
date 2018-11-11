"""
    povpi/views.py
    Index Views
"""

import json

import boto3
from flask import redirect, render_template, request, url_for

from povpi import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/change', methods=["POST"])
def change():
    msg = {
        "state": {
            "desired": {
                "display": request.form['display']
            }
        }
    }
    client = boto3.client('iot-data', 'us-east-2')
    client.publish(topic='$aws/things/POVRPi/shadow/update',
                   payload=json.dumps(msg), qos=1)
    return redirect(url_for('index'))


@app.route('/toggle', methods=["POST"])
def toggle():
    toggle = [k for k in request.form.keys()][0]
    enabled = True if toggle == "on" else False
    shadow = {
        "state": {
            "desired": {
                "enabled": enabled
            }
        }
    }
    payload = json.dumps(shadow)
    client = boto3.client('iot-data', 'us-east-2')
    client.publish(topic='$aws/things/POVRPi/shadow/update',
                   payload=payload, qos=1)
    return redirect(url_for('index'))
