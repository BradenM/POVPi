"""
    povpi
    Entry file for Persistence of Vision Pi
"""

from flask import Flask
from flask_cors import CORS

app = Flask(__name__, static_folder="./static/dist",
            template_folder="./static")
app.config.from_object('povpi.config')
CORS(app)

import povpi.views