"""
    povpi/views.py
    Index Views
"""

from povpi import app
from flask import render_template, request, url_for, redirect
import boto3
import json


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/change', methods=["POST"])
def change():
    msg = {
        'topic': 'povRPi/display',
        'payload': {'message': request.form['display']}
    }
    client = boto3.client('iot-data', 'us-east-2')
    client.publish(topic='povRPi/display', payload=json.dumps(msg), qos=1)
    return redirect(url_for('index'))
