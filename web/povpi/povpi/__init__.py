"""
    povpi
    Entry file for Persistence of Vision Pi
"""

from flask import Flask

app = Flask(__name__)
app.config.from_object('povpi.config')

import povpi.views