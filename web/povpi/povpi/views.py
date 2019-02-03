"""
    povpi/views.py
    Index Views
"""

import json

import boto3
from flask import redirect, render_template, request, url_for, jsonify

from povpi import app

client = boto3.client('iot-data', 'us-east-2')


@app.route('/')
def index():
    js_bundle = "https://s3.us-east-2.amazonaws.com/povpi-resources/js/bundle.js"
    if app.config['DEBUG']:
        js_bundle = "dist/bundle.js"
    return render_template('index.html', bundle_url=js_bundle)


@app.route('/change', methods=["POST"])
def change():
    req = request.get_json()
    msg = {
        "state": {
            "desired": {
                "display": req['message']
            }
        }
    }
    client.publish(topic='$aws/things/POVRPi/shadow/update',
                   payload=json.dumps(msg), qos=1)
    return redirect(url_for('index'))


@app.route('/toggle', methods=["POST"])
def toggle():
    req = request.get_json()
    shadow = {
        "state": {
            "desired": {
                "enabled": req['state']
            }
        }
    }
    payload = json.dumps(shadow)
    client.publish(topic='$aws/things/POVRPi/shadow/update',
                   payload=payload, qos=1)
    return redirect(url_for('index'))


@app.route('/getshadow', methods=['GET'])
def get_shadow():
    shadow_req = client.get_thing_shadow(thingName='POVRPi')['payload']
    shadow = json.loads(shadow_req.read())
    shadow_state = shadow['state']
    return jsonify(shadow_state['desired'])
